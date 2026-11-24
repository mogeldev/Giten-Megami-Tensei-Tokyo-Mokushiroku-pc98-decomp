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
    ("nop-padded branch", lambda b: b"\xeb\x03\x90" in b or b"\xeb\x02\x90" in b
                                       or b"\x74\x03\x90" in b or b"\x75\x03\x90" in b,
     "the original pads a short jump with a `90` before the next block (`EB 03 90 33 C0`); "
     "MSC 7 emits the jump without padding, so every following branch distance differs by one"),
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
