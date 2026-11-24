#!/usr/bin/env python3
"""classify.py - sort the unmatched units by *why* they do not match yet.

Every remaining unit is a candidate for a future round, but most of them are not
blocked by a missing source shape: they contain a code-generation idiom that no
available compiler reproduces (the original was built by an older Microsoft C).
This tool recognises the known idioms and writes docs/BLOCKED.md so that each
unit is classified once instead of being re-derived every round.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]

# (label, predicate, note)
TRAITS = [
    ("fragment (no prologue)", lambda b: not (b[:3] == b"\x55\x8b\xec" or b[:1] == b"\xc8"),
     "the unit does not start with a function prologue, so the inventory window began "
     "in the middle of a routine: it cannot be matched as a function at all"),
    ("ENTER frame", lambda b: b[:1] == b"\xc8",
     "`C8 xx xx 00` prologue - the original never uses ENTER; MSC 7 only emits "
     "it with /Gs plus a local, so these come from the older compiler"),
    ("inline long shift", lambda b: b"\x8a\xe0\x2a\xc0" in b,
     "the original inlines a 32-bit `x << 8` as `mov ah,al` / `sub al,al` (and the high "
     "word with `mov dh,dl` / `mov dl,ah`); MSC 7 calls the shift helper for the same "
     "expression (`9A __aFulshl`), so any unit doing long shifts is unreachable"),
    ("register variable in BX",
     lambda b: b[:4] == b"\x55\x8b\xec\x53",
     "the original pushes BX in the prologue, i.e. it uses BX as a callee-saved register "
     "variable; MSC 7 only allocates SI and DI and treats BX as scratch, so any unit that "
     "preserves BX cannot be reproduced. Verified on 11a2:000c, where the whole body "
     "matches once the pointer is near and the callee fastcall"),
    ("frame without frame use",
     lambda b: b[:3] == b"\x55\x8b\xec" and not re.search(
         rb"(?:\x8b|\x89|\x8a|\x88|\xc7|\xc6|\xff|\x83|\x81|\x3b|\x39|\x03|\x2b|\x0b|\x01"
         rb"|\x29|\x21|\x31|\x09|\x11|\x19|\xf7|\xd1)[\x46\x4e\x56\x5e\x66\x6e\x76\x7e]",
         b[3:]) and (b.endswith(b"\xc3") or b.endswith(b"\xcb")
                     or (len(b) >= 4 and b[-3] in (0xca, 0xc2))),
     "the unit opens with a frame and never references `[bp+nn]`, so the function has no "
     "parameters and no locals: the original still emits `55 8B EC` while MSC omits the "
     "frame entirely (verified on 1270:000e; /G0 and /Gd both keep it frameless)"),
    ("sub ax,ax zeroing",
     lambda b: b"\x2b\xc0" in b or b"\x2a\xe4" in b or b"\x2a\xc0" in b or b"\x2b\xc9" in b,
     "**not a wall for the `2A E4` form**: round 146 verified that MSC 7 emits `2A E4` for a "
     "`(unsigned char)` load (`int f(unsigned i) { return (unsigned char)g[i]; }`), and for a "
     "byte field of a struct with `>1` alignment. Only the `sub ax,ax` / `sub cx,cx` forms are "
     "unreachable (MSC emits `33 C0`), and `4344:000e` differs from its transcription only in "
     "instruction order (`C1 E3 02 2A E4 8A 87` versus `C1 E3 02 8A 87 ... 2A E4`)"),
    ("byte argument without promotion",
     lambda b: re.search(rb"(?:\x8a\x46[\x00-\xff]\x50|\xa0[\x00-\xff][\x00-\xff]\x50)", b) is not None,
     "the original pushes a `char` argument straight from the byte it loaded (`8A 46 <n>` + `50`, "
     "or `A0 <disp>` + `50`) with no `cbw`/`sub ah,ah`; MSC 7 always promotes (`98` or `2A E4` first), "
     "so every such call site diverges by one or two bytes. Verified on 2127:000c and 2daa:001c"),
    ("nop-padded branch", lambda b: re.search(rb"\xeb[\x00-\x7f]\x90", b) is not None
                                       or b"\x74\x03\x90" in b or b"\x75\x03\x90" in b,
     "the original pads a short jump with a `90` before the next block (`EB 03 90 33 C0`, "
     "`EB 0E 90`); MSC 7 emits the jump without padding, so every following branch distance "
     "differs by one. Verified by full analysis on 4998:000c, 3b88:000e, 31e3:0064, 3cd1:02f2 "
     "and 3b9b:000a; the pattern itself is a heuristic (185 units match it)"),
    ("jump-merge boolean", lambda b: b"\xeb\x03\xb8\x01\x00" in b or b"\xeb\x02\x33\xc0" in b
                                 or b"\x33\xc0\xeb" in b or b"\x99\xeb" in b,
     "`jz/...; xor ax,ax; jmp; mov ax,1` merge - MSC 7 always uses `sbb/inc` or early returns"),
    ("add reg,reg doubling", lambda b: any(b[i:i+2] in (b"\x03\xc0", b"\x03\xc6", b"\x03\xd2",
                                                        b"\x03\xdb", b"\x03\xc9", b"\x03\xff")
                                            for i in range(len(b) - 1)),
     "`add ax,ax`-style doubling for `x * 2` - MSC 7 uses `shl`"),
    ("inlined MK_FP", lambda b: b"\x8e\x06" in b or b"\x8e\xc0" in b,
     "`mov es,[disp16]` or `mov es,ax` right before an ES-relative access - the "
     "original inlines `MK_FP(seg, off)` (with a global or a parameter segment); "
     "MSC 7 calls the `MK_FP` helper and then does `mov es,dx`"),
    ("far pointer in a register pair", lambda b: b"\xc5\x5e" in b or b"\xc5\x5f" in b
                                        or b"\xc4\x76" in b or b"\xc4\x7e" in b,
     "`lds bx,[bp+..]` - the original keeps a far pointer in DS:BX across a loop "
     "and tests it with `mov ax,ds; or ax,bx`; MSC 7 keeps it in the stack frame"),
    ("split far-pointer load", lambda b: b"\x8e\x46" in b or b"\x8e\x4e" in b,
     "`mov es,[bp+xx]` loading only the segment half of a far pointer - blocked trait"),
    ("chkstk preamble", lambda b: b"\xb8\x00\x00" in b and b"\x9a" in b,
     "`B8 00 00 9A` stack-probe call - MSC 7 with a far data threshold, never in the original"),
    ("ES absolute access", lambda b: b"\x26\xa1" in b or b"\x26\xa3" in b,
     "`mov ax,es:[disp16]` - MSC 7 emits `les bx` + `es:[bx]` instead"),
    ("inline interrupt", lambda b: b"\xcd\x21" in b or b"\xcd\x2f" in b or b"\xcd\x31" in b,
     "an inline `int 21h` / `int 2Fh` / `int 31h` - the original issues DOS, multiplex "
     "or DPMI calls in line; MSC 7 only offers library wrappers (`intdos`, `int86`), "
     "so these are hand-written or builtin-generated"),
    ("AH argument", lambda b: re.search(b"\xb4[\x00-\xff][^\\x00]{0,6}\x9a", b, re.S) is not None,
     "`mov ah,imm` before a far call - an argument in AH, a DOS/EMS register "
     "convention the original used and MSC 7 cannot be told to produce"),
    ("redundant or reg,ax", lambda b: re.search(b"\x8b[\xf0-\xff]\x0b[\xf0\xc0-\xff]", b, re.S) is not None,
     "`mov si,ax; or si,ax` - older codegen tests the just-moved value again"),
    ("string walk (lodsb/stosb)", lambda b: b"\xac" in b and b"\xaa" in b and b"\xe2" in b,
     "hand-optimised byte loops (`lodsb` / `stosb` / `loop`) - MSC 7 always addresses "
     "through `26 8A 07` / `26 88 07` and keeps the pointers in the frame"),
    ("rep stosw memset", lambda b: b"\xf3\xab" in b,
     "word-fill inline `memset` - MSC 7 with /Oi emits `rep stosb`"),
    ("CX-staged value", lambda b: b"\x8b\x4e" in b and b"\x51" in b,
     "a value is compared and then pushed: the original loads it into **CX** once "
     "(`8B 4E xx`) and reuses it (`cmp cx,..`, `or ch,..`, `push cx`), while MSC 7 "
     "compares from memory and pushes the slot again"),
    ("operand order", lambda b: b"\x0b\xc7" in b or b"\x0b\xc6" in b,
     "`or ax,di` where MSC 7 canonicalises to loading the register operand first"),
]

ROW = re.compile(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", re.M)


def main():
    led = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    done = {int(m.group(1), 16) * 16 + int(m.group(2), 16) for m in ROW.finditer(led)}
    crt = {int(r["linear"], 16) for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "foreign_crt.csv")))}

    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))

    buckets = {label: [] for label, _p, _n in TRAITS}
    buckets["unclassified"] = []
    for lin, (va, size) in units.items():
        if lin in done or lin in crt:
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size]
        core = b.rstrip(b"\x90")
        # only whole functions: the window must end at a return
        if not core or not (core[-1] in (0xC3, 0xCB) or (len(core) >= 3 and core[-3] in (0xCA, 0xC2))):
            continue
        b = core
        hit = False
        for label, pred, _note in TRAITS:
            try:
                if pred(b):
                    buckets[label].append((size, va))
                    hit = True
                    break
            except Exception:
                pass
        if not hit:
            buckets["unclassified"].append((size, va))

    notes = {label: note for label, _p, note in TRAITS}
    notes["unclassified"] = ("no known blocker - these are the real candidates for "
                             "new source shapes")
    lines = ["# BLOCKED", "",
             "Generated by `tools/classify.py` - every unmatched whole function sorted",
             "by the code-generation idiom that prevents a match. Regenerate after each",
             "round. Counts may include segment aliases (the inventory lists some code",
             "under two spellings), so treat them as an upper bound.",
             ""]
    total = sum(len(v) for v in buckets.values())
    lines.append(f"{total} unmatched units (excluding CRT and verified).")
    lines.append("")
    lines.append("| class | units | bytes | why it stays open |")
    lines.append("|---|---|---|---|")
    for label in sorted(buckets, key=lambda k: -sum(s for s, _ in buckets[k])):
        v = buckets[label]
        if not v:
            continue
        lines.append(f"| {label} | {len(v)} | {sum(s for s, _ in v)} | {notes[label]} |")
    lines.append("")
    for label in sorted(buckets, key=lambda k: -sum(s for s, _ in buckets[k])):
        v = buckets[label]
        if not v:
            continue
        v.sort(reverse=True)
        lines.append(f"## {label} ({len(v)} units, {sum(s for s, _ in v)} bytes)")
        lines.append("")
        lines.append(notes[label])
        lines.append("")
        lines.append("Largest: " + ", ".join(f"`{va}` ({s} B)" for s, va in v[:12]))
        lines.append("")
    out = os.path.join(ROOT, "docs", "BLOCKED.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"BLOCKED.md written: {total} unmatched units across {len([1 for v in buckets.values() if v])} classes")
    for label in sorted(buckets, key=lambda k: -sum(s for s, _ in buckets[k])):
        v = buckets[label]
        if v:
            print(f"  {label}: {len(v)} units, {sum(s for s, _ in v)} bytes")


if __name__ == "__main__":
    main()
