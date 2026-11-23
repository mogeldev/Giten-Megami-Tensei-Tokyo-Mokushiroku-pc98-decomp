#!/usr/bin/env python3
"""mine.py [--min N] [--max N] — candidate finder (template phase 5, step 1).

Prints small functions whose decompiled body contains no calls, no loops and no
jumps, i.e. candidates that can be transcribed by hand. Each line carries the
inventory name, size, raw bytes and the decompiled body so the form is visible.

Usage: python tools/mine.py > build/candidates.txt
"""
import argparse
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = os.path.join(ROOT, "..", "decompiled", "DDS98_decompiled.c")
BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16
HEAD_RE = re.compile(r"(\S+) @ ([0-9a-f]{4}):([0-9a-f]{4}) \*\*\*\*/\s*\n(.*?)(?=\n\n\n|\Z)", re.S)


def mine_units(a):
    """Candidate finder over the split inventory (units hidden inside blobs)."""
    import csv as _csv
    img = open(BIN, "rb").read()[HDR:339735]
    ledger = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    done = {int(m.group(1), 16) * 16 + int(m.group(2), 16)
            for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", ledger, re.M)}
    out = []
    for r in _csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        lin, size = int(r["linear"], 16), int(r["size"])
        if r["parent"] == r["va"]:      # already reachable via functions.csv
            continue
        if lin in done or not a.min <= size <= a.max:
            continue
        b = img[lin - 0x10000: lin - 0x10000 + size]
        if any(x in b for x in (0xE8, 0x9A, 0xCD, 0xEB, 0xE9)):
            continue
        if b[-1] not in (0xC3, 0xCB) and b[-3:-1] not in (b"\xCA", b"\xC2"):
            continue
        out.append((size, r["va"], b.hex()))
    out.sort()
    print(f"# {len(out)} hidden units call-free and jump-free ({a.min}..{a.max} bytes)")
    for size, va, hx in out:
        print(f"{va}\t{size:>2}\t{hx}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=5)
    ap.add_argument("--max", type=int, default=24)
    ap.add_argument("--units", action="store_true",
                    help="use ground_truth/units.csv (split inventory: includes the "
                         "functions merged into bigger entries). No decompiled text is "
                         "available for those, so candidates are filtered on bytes only.")
    a = ap.parse_args()

    if a.units:
        return mine_units(a)

    src = open(DEC, encoding="utf-8", errors="replace").read()
    img = open(BIN, "rb").read()[HDR:339735]
    inv = {r["name"]: r for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "functions.csv")))}
    ledger = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    # Dedupe by LINEAR address: Ghidra lists the same code under several seg:off
    # names, so a name-based check lets aliases of matched functions through.
    done_lin = set()
    for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", ledger, re.M):
        done_lin.add(int(m.group(1), 16) * 16 + int(m.group(2), 16))

    found = []
    for ch in src.split("/**** ")[1:]:
        m = HEAD_RE.match(ch)
        if not m:
            continue
        name, seg, off, body = m.groups()
        va = f"{seg}:{off}"
        lin = int(seg, 16) * 16 + int(off, 16)
        if lin in done_lin or name not in inv:
            continue
        size = int(inv[name]["size"])
        if not a.min <= size <= a.max:
            continue
        if re.search(r"\b(FUN_|swi|while|for|goto|switch)\b", body):
            continue
        b = img[lin - 0x10000:lin - 0x10000 + size]
        if 0xE8 in b or 0x9A in b or 0xCD in b or 0xEB in b or 0xE9 in b:
            continue
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        # skip pure epilogues / prologues
        code = " | ".join(lines[1:])
        found.append((size, va, name, b.hex(), code))

    found.sort()
    print(f"# {len(found)} call-free, jump-free candidates ({a.min}..{a.max} bytes)")
    for size, va, name, hx, code in found:
        print(f"{va}\t{size:>2}\t{name}\t{hx}\t{code[:160]}")


if __name__ == "__main__":
    main()
