#!/usr/bin/env python3
"""match.py <va> <symbol> --obj <file> [--size N] — byte-match harness (template phase 3).

Compares a symbol from an MSC-7 OMF object against the original bytes of
DDS98.EXE and classifies:
  MATCH  = identical
  RELOCS = identical except for byte positions with an OMF fixup (linker operands)
  DIFF   = byte diffs with original and own instruction
Size: inventory distance to the next function; --size overrides; 0 forbidden.
Fixups are read from the object (MSC-7 compact 0x9C records, see omfdump.py)
and never guessed. Without --obj: abort with a hint to build.py (layout convention
follows as soon as real subsystem source files exist)."""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import omfdump  # noqa: E402

BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16          # MZ header size (file offset of the load image)
IMG_BASE = 0x10000      # Ghidra mapping: segment 0x1000:0000


def linear(va):
    va = va.strip().lower()
    if ":" in va:
        s, o = va.split(":")
        return (int(s, 16) << 4) + int(o, 16)
    return int(va, 16)


def compare(orig, mine, relocs):
    """(status, diffs, masked) plus a shrink note. relocs = linker operands.

    `orig` is the image window (its length is the ledger size), `mine` is the
    object slice and may be one byte longer: LINK /F folds a same-segment far
    call into `0E E8 rel16` (4 B) where the object still has `9A seg off`
    (5 B), so the whole tail shifts by one."""
    for shrink_at in shrink_sites(orig, mine, relocs):
        status, diffs, masked = _walk(orig, mine, relocs, shrink_at)
        if status != "DIFF":
            return status, diffs, masked, shrink_at
    # the caller slices one byte extra for the folded-call case; without a
    # shrink site that byte is simply not part of the comparison
    status, diffs, masked = _walk(orig, mine[:len(orig)], relocs, None)
    return status, diffs, masked, None


FAR_SHORT = b"\x0E\xE8"               # same-segment far call: PUSH CS; CALL NEAR


def shrink_sites(orig, mine, relocs):
    """Image offsets where a 4-byte `0E E8` stands for the object's 5-byte 9A."""
    if len(mine) != len(orig) + 1:
        return []
    out = []
    for i in range(len(orig) - 1):
        if mine[i] != 0x9A or not all((i + 1 + k) in relocs for k in range(4)):
            continue
        if orig[i:i + 2] == FAR_SHORT:
            out.append(i)
    return out


def _walk(orig, mine, relocs, shrink_at):
    """Compare with an optional 5->4 byte shrink at image offset `shrink_at`."""
    diffs, masked = [], 0
    i = j = 0
    while i < len(orig):
        if shrink_at is not None and i == shrink_at:
            i += 4        # 0E E8 rel16
            j += 5        # 9A seg off
            masked += 5
            continue
        if (i + 2 < len(orig) and orig[i:i + 3] == FAR_TRANSLATED
                and j < len(mine) and mine[j] == 0x9A
                and all((j + 1 + k) in relocs for k in range(4))):
            i += 5
            j += 5
            masked += 5
            continue
        if j < len(mine):
            if j in relocs:
                masked += 1
            elif orig[i] != mine[j]:
                diffs.append((i, orig[i], mine[j]))
            i += 1
            j += 1
        else:
            diffs.append((i, "LEN", f"{len(orig)} vs {len(mine)}"))
            break
    if j != len(mine) and not diffs:
        diffs.append((min(len(orig), len(mine)), "LEN", f"{len(orig)} vs {len(mine)}"))
    if not diffs:
        return ("RELOCS" if masked else "MATCH"), diffs, masked
    return "DIFF", diffs, masked


FAR_TRANSLATED = b"\x90\x0E\xE8"      # LINK /FARCALLTRANSLATION: NOP; PUSH CS; CALL


def farcall_translated(orig, mine, relocs):
    """Offsets covered by LINK /F's far-call rewriting.

    With /FARCALLTRANSLATION (and /PACKC the callee ends up in the caller's
    physical segment), the linker rewrites a direct far call `9A seg off`
    (5 bytes) into `90 0E E8 rel16` (5 bytes, NOP + PUSH CS + CALL NEAR, see
    MSKB S9BJ7). The object keeps the 9A form with a 4-byte fixup; the image
    has the translated form whose rel16 is link-layout dependent.

    A site counts only if the object byte is 9A with its whole 4-byte operand
    masked AND the image has exactly `90 0E E8` there — a wrong call target
    still differs, only the opcode form is accepted as translated."""
    out = set()
    for i in range(min(len(orig), len(mine)) - 4):
        # the OMF fixup covers the 4-byte operand only, not the 0x9A opcode
        if mine[i] == 0x9A and all((i + 1 + k) in relocs for k in range(4)):
            if orig[i:i + 3] == FAR_TRANSLATED:
                out.update(range(i, i + 5))
    return out


def selftest():
    a = bytes(range(64))
    st, d, m, sh = compare(a, a, set())
    assert st == "MATCH" and not d and m == 0 and sh is None
    b = bytearray(a)
    b[4] ^= 1
    st, d, _, _ = compare(a, bytes(b), set())
    assert st == "DIFF" and d[0][0] == 4
    st, d, m, _ = compare(a, bytes(b), {4})
    assert st == "RELOCS" and m == 1 and not d
    st, d, m, _ = compare(a, a, {7, 9})
    assert st == "RELOCS" and m == 2
    st, d, m, _ = compare(a, a[:60], set())
    assert st == "DIFF" and d[0][1] == "LEN"
    # LINK /F translation: object 9A + 4 masked bytes vs image 90 0E E8 rel16
    orig = bytes(10) + FAR_TRANSLATED + b"\x34\x12" + bytes(3)
    mine = bytes(10) + b"\x9A" + b"\x00\x00\x00\x00" + bytes(3)
    rels = set(range(11, 15))
    st, d, _, _ = compare(orig, mine, rels)
    assert st == "RELOCS" and not d, (st, d)
    # ... only when the image really has the translated form at that site
    bad = bytearray(orig)
    bad[10] = 0x0E
    st, d, _, _ = compare(bytes(bad), mine, rels)
    assert st == "DIFF" and d[0][0] == 10
    # ... and only for calls whose operand is a full 4-byte fixup
    st, d, _, _ = compare(orig, mine, set(range(12, 15)))
    assert st == "DIFF"
    # folded same-segment far call: image 0E E8 rel16 (4 B) vs object 9A + 4 (5 B)
    img = b"\x55\x8B\xEC" + FAR_SHORT + b"\x12\x34" + b"\xCB"      # 8 bytes
    obj = b"\x55\x8B\xEC" + b"\x9A\x00\x00\x00\x00" + b"\xCB"  # 9 bytes
    st, d, m, sh = compare(img, obj, {4, 5, 6, 7})
    assert st == "RELOCS" and not d and sh == 3 and m == 5, (st, d, sh)
    # negative: the tail must really match after the shift
    badobj = bytearray(obj)
    badobj[8] = 0xCC
    st, d, _, _ = compare(img, bytes(badobj), {4, 5, 6, 7})
    assert st == "DIFF"
    print("selftest OK: MATCH/RELOCS/DIFF, reloc masking, length diff, "
          "/F call translation, 5->4 byte folded far call")


def load_funcs():
    with open(os.path.join(ROOT, "ground_truth", "functions.csv")) as f:
        return {int(r["linear"], 16): int(r["size"]) for r in csv.DictReader(f)}


def binary_bytes(lin, size):
    data = open(BIN, "rb").read()
    off = lin - IMG_BASE + HDR
    if off < 0 or off + size > 339735:
        sys.exit(f"ERROR: {lin:#x} outside the load image")
    return data[off: off + size]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("va", nargs="?")
    ap.add_argument("symbol", nargs="?")
    ap.add_argument("--obj")
    ap.add_argument("--size", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    if not a.va or not a.symbol or not a.obj:
        ap.error("va, symbol and --obj required (or --selftest)")

    lin = linear(a.va)
    funcs = load_funcs()
    size = a.size if a.size else funcs.get(lin, 0)
    if size <= 0:
        sys.exit(f"ERROR: {a.va} not in the inventory or size 0 — "
                 "run tools/gt.py first; a 0-byte match is forbidden")

    ledatas, pubdefs = omfdump.load(a.obj)
    # C symbols get a leading underscore, __fastcall ones a leading '@'
    sym = next((s for s in (a.symbol, "_" + a.symbol, "@" + a.symbol)
                if s in pubdefs), None)
    if sym is None:
        # round 111: __pascal and __cdecl mangle differently (F_xxx vs _f), and a
        # case-only difference has cost several rounds a retry - fall back to it
        low = a.symbol.lower()
        sym = next((s for s in pubdefs if s.lower() in (low, "_" + low, "@" + low)), None)
    if sym is None:
        sys.exit(f"ERROR: symbol '{a.symbol}' not in object "
                 f"(present: {', '.join(sorted(pubdefs))})")
    seg, off = pubdefs[sym]
    led = next((l for l in ledatas if l["seg"] == seg), None)
    if led is None:
        sys.exit(f"ERROR: no LEDATA for segment {seg}")
    code = led["data"][off: off + size + 1]     # +1 for a folded far call (5->4)
    if len(code) < size:
        sys.exit(f"ERROR: symbol at end of LEDATA — size {size} too large")
    relocs = {(o + k) - off for (o, s) in led["fixups"]
              if off <= o < off + size + 1 for k in range(s)}

    orig = binary_bytes(lin, size)
    status, diffs, masked, shrink_at = compare(orig, code, relocs)
    extra = f", folded far call at +{shrink_at:#x}" if shrink_at is not None else ""
    print(f"{a.va} {a.symbol}: {status}  (size={size}, reloc-masked={masked}{extra})")
    for (o, ob, mb) in diffs[:12]:
        if isinstance(ob, int):
            print(f"  DIFF @+{o:#x}: orig {ob:02X} vs object {mb:02X}")
        else:
            print(f"  DIFF @+{o:#x}: {ob} {mb}")
    sys.exit(0 if status in ("MATCH", "RELOCS") else 1)


if __name__ == "__main__":
    main()
