"""twins.py - find unrecorded byte-identical twins of ledger functions.

For every MATCH/RELOCS row, search the load image for the same byte sequence at a
known unit start that is not already in the ledger. A twin is a free row: the
same source verifies it once `match.py` confirms it.

Note: the comparison uses the ORIGINAL bytes including the disp16 operands, so a
twin touches exactly the same globals as the recorded function.
"""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
units = {}
for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
    units[int(r["linear"], 16)] = (r["va"], int(r["size"]))

rows = []
visited = set()
for line in open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8"):
    m = re.match(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(MATCH|RELOCS)", line)
    if not m:
        continue
    seg, off, name, size, status = m.groups()
    lin = int(seg, 16) * 16 + int(off, 16)
    rows.append((lin, name, int(size), status))
    visited.add(lin)

found = []
for lin, name, size, status in rows:
    b = IMG[lin - 0x10000: lin - 0x10000 + size]
    if not b or len(b) != size:
        continue
    start = 0
    while True:
        p = IMG.find(b, start)
        if p < 0:
            break
        start = p + 1
        tlin = p + 0x10000
        if tlin == lin or tlin in visited:
            continue
        if tlin not in units:          # must be a known unit boundary
            continue
        found.append((units[tlin][0], name, size, status))

print(f"{len(found)} unrecorded twins of ledger functions")
for va, name, size, status in found:
    print(f"  {va}  size {size:>3}  same as {name} ({status})")
