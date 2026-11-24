"""List units whose inventory window cuts the function short.

`units.csv` sizes are not always the real function extent: round 109's `4dca:000c` is
declared 28 bytes but is 34, with the window ending inside its last far call. Such
units were filed as "fragments" and never attempted. This finds them: the window does
not end at a return, but a return follows within 64 bytes with no `55 8B EC` prologue
in between (which would mean a different function starts first).

    python tools/cutwin.py [--limit N]
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]


def ends_ret(c):
    # any `ret imm16` / `retf imm16`, not just the zero-pop forms (round 110: the
    # earlier `c[-2] == 0` test rejected retf 2 / retf 4 / ... and made complete
    # functions look cut)
    return (c.endswith(b"\xc3") or c.endswith(b"\xcb")
            or (len(c) >= 4 and c[-3] in (0xCA, 0xC2)))


def main():
    crt = {int(r["linear"], 16) for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "foreign_crt.csv")))}
    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))
    led = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    done = {int(m.group(1), 16) * 16 + int(m.group(2), 16)
            for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", led, re.M)}

    def first_ret(base, limit):
        # Round 110: scan from the unit start for the first return, rather than
        # extending from the window end.  A return *inside* the window means the
        # function is complete (the window merely overshoots), which the earlier
        # forward-extension version mis-reported as a cut.
        for n in range(3, limit):
            c = IMG[base:base + n]
            if ends_ret(c):
                return n
        return None

    out = []
    for lin, (va, size) in units.items():
        if lin in done or lin in crt or size < 10:
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size].rstrip(b"\x90")
        if b[:3] != b"\x55\x8b\xec":
            continue
        if first_ret(lin - 0x10000, size) is not None:
            continue                      # complete inside the window
        real = first_ret(lin - 0x10000, size + 64)
        if real is not None and real > size:
            body = IMG[lin - 0x10000 + 3: lin - 0x10000 + real]
            if b"\x55\x8b\xec" not in body:
                out.append((real, va, size))

    out.sort()
    print(f"# {len(out)} units whose window cuts the function ({sum(o[0] for o in out)} B)")
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 15
    for real, va, size in out[:limit]:
        print(f"{va}\tunit={size}\treal={real}")


if __name__ == "__main__":
    main()
