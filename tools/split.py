#!/usr/bin/env python3
"""split.py — recover function boundaries that the inventory merged.

`ground_truth/functions.csv` was produced by the decompiler and merges several
real functions into one entry whenever a gap byte interrupts its flow (measured:
189 entries hide 2..6 units each). This tool re-scans every CODE entry and writes
`ground_truth/units.csv` with the recovered units.

Detection rule (conservative, so the result is a LOWER bound):
    terminator  := optional C9 followed by CB | C3 | CA imm16 | C2 imm16
    gap         := 0 .. 2 zero bytes
    next unit   := starts with 55 8B EC (frame), C8 xx xx 00 (enter) or
                   A1 xx xx followed by CB/C3 (short word getter)
A hit only counts when the terminator, the gap and the prologue line up.

Usage:
  python tools/split.py                # write ground_truth/units.csv
  python tools/split.py --selftest     # assert the three known blobs
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16
IMG_END = 339735

# The unit ends at the terminator; the gap bytes are captured so the NEXT unit
# starts after them. Unit lengths therefore stay gap-free.
#
# Prologue alternatives, widened in two steps (rounds 43/44) by measuring how many
# boundaries each opcode would add and eyeballing the surrounding bytes:
#   55 8B EC / enter         framed entry
#   A1 / A0 / 8B 16 / 8B 0E / 8B 36 / 8B 3E / 8B 1E   word/byte loads from disp16
#   A3 / A2 / 89 06 / C7 06 / C6 06                  stores to disp16
#   FF 06 / FF 0E / FF 36                            inc / dec / push
#   B8 .. / 80 0E / 26 89                            load imm / or byte / es: mov
# Deliberately NOT included: `31` (xor) - measurement showed it fires in the
# middle of functions (`31 46 FE` = xor [bp-2],ax).
TERM = re.compile(rb"(?:\xC9)?(?:\xCB|\xC3|\xCA..|\xC2..)(\x00{0,2})"
                  rb"(?=(\x55\x8B\xEC|\xC8..\x00|\xA1..|\xA0..|\x8B\x16|\x8B\x0E"
                  rb"|\x8B\x36|\x8B\x3E|\x8B\x1E|\xA3..|\xA2..|\x89\x06|\xC7\x06"
                  rb"|\xC6\x06|\xFF\x06|\xFF\x0E|\xFF\x36|\xB8..|\x80\x0E"
                  rb"|\x26\x89))", re.S)

# regression check: linear address of the FIRST unit -> expected unit count
EXPECTED = {
    0x31e3C: 5,   # 31e3:000c - four 21-byte wrappers + one conditional
    0x4C93A: 3,   # 458e:705a - two exchanges + getter
    0x4DF22: 3,   # 458e:8642 - shadow copy + setter + copy back
    0x3E24C: 4,   # host entry starts earlier: 95 B prefix + get / inc+get / dec+get
    0x1F2DE: 1,   # clamp with early return: a jump targets the inner return, so NOT a boundary
}


def load_img():
    return open(BIN, "rb").read()[HDR:IMG_END]


def split_entry(img, lin, size):
    """Return list of (offset, length) units inside one inventory entry."""
    b = img[lin - 0x10000: lin - 0x10000 + size]
    units, cur = [], 0
    for m in TERM.finditer(b):
        gap = len(m.group(1))
        term_end = m.end() - gap          # unit ends here, gap excluded
        if term_end <= cur or term_end > size:
            continue
        start = m.end()                   # next unit starts after the gap
        # An EARLY RETURN inside one function looks exactly like a boundary: the
        # next block begins with a known prologue. It is not a boundary if a
        # short jump from the current block targets it (round 45: the clamp
        # `if (v < 1) return 1; ...` produced a bogus split).
        if _jumped_to(b[cur:start], start - cur):
            continue
        units.append((cur, term_end - cur))
        cur = start
    if cur < size:
        units.append((cur, size - cur))
    return units


def _jumped_to(block, target):
    """True if a short jump inside `block` lands exactly on `target`."""
    for i in range(len(block) - 1):
        op = block[i]
        if op == 0xEB or 0x70 <= op <= 0x7F:
            disp = block[i + 1] - 256 if block[i + 1] > 127 else block[i + 1]
            if i + 2 + disp == target:
                return True
    return False


def rows():
    return [r for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "functions.csv")))
            if r.get("section") != "DATA"]


def selftest():
    img = load_img()
    entries = [(int(r["linear"], 16), int(r["size"])) for r in rows()]
    bad = 0
    for target, want in EXPECTED.items():
        host = [e for e in entries if e[0] <= target < e[0] + e[1]]
        if not host:
            print(f"  0x{target:x}: not inside any inventory entry FAIL")
            bad += 1
            continue
        _, size = host[0]
        units = split_entry(img, target, size)
        got = len(units)
        status = "ok" if got == want else "FAIL"
        if got != want:
            bad += 1
        print(f"  0x{target:x}: {got} units (expected {want}) {status}  sizes={[u[1] for u in units]}")
    # invariant: units must tile the entry exactly
    host = [e for e in entries if e[0] <= 0x31E3C < e[0] + e[1]][0]
    units = split_entry(img, 0x31E3C, host[1])
    # gap bytes belong to no unit, so the sizes may be short by 0..2 per boundary
    slack = host[1] - sum(u[1] for u in units)
    if not 0 <= slack <= 2 * (len(units) - 1):
        print(f"  FAIL: unit sizes do not add up (slack {slack})")
        bad += 1
    print("split selftest:", "ok" if not bad else f"{bad} failure(s)")
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())

    img = load_img()
    out, hidden = [], 0
    for r in rows():
        lin, size = int(r["linear"], 16), int(r["size"])
        units = split_entry(img, lin, size)
        if len(units) > 1:
            hidden += len(units) - 1
        for off, ln in units:
            va = f"{(lin + off) >> 4:04x}:{(lin + off) & 0xF:04x}"
            if len(units) > 1:
                va = f"{r['va'].split(':')[0]}:{int(r['va'].split(':')[1], 16) + off:04x}"
            out.append({"va": va, "linear": f"0x{lin + off:x}", "size": ln,
                        "parent": r["va"], "name": r["name"] if len(units) == 1 else
                        f"{r['name']}_u{off}"})

    dst = os.path.join(ROOT, "ground_truth", "units.csv")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["va", "linear", "size", "parent", "name"])
        w.writeheader()
        w.writerows(out)
    print(f"units.csv written: {len(out)} units from {len(rows())} inventory entries "
          f"({hidden} hidden units recovered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
