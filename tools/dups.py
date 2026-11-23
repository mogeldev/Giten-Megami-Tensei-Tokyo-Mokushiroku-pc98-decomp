"""Find byte-identical duplicated units (fixed terminator test).

A duplicate is worth more than a single match: one transcription verifies every
address in the group. Bytes must be identical INCLUDING the disp16 operands, so
the duplicates touch the same globals - genuine copy/paste.

Terminator test (the round-49 version was wrong): a unit ends with
  CB / C3            at b[-1], or
  CA imm16 / C2 imm16 at b[-3] (the opcode, not b[-2] as the first draft assumed).
"""
import csv
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
units = {}
for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
    units[int(r["linear"], 16)] = (r["va"], int(r["size"]))
ledger = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
done = {int(m.group(1), 16) * 16 + int(m.group(2), 16)
        for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", ledger, re.M)}


def is_unit(b):
    if not b:
        return False
    if b[-1] in (0xC3, 0xCB):
        return True
    return len(b) >= 4 and b[-3] in (0xCA, 0xC2)


groups = defaultdict(list)
for lin, (va, size) in units.items():
    if lin in done or not 6 <= size <= 80:
        continue
    b = IMG[lin - 0x10000: lin - 0x10000 + size]
    if len(b) != size or not is_unit(b):
        continue
    groups[b].append((va, size))

dups = sorted(((b, m) for b, m in groups.items() if len(m) >= 2), key=lambda x: -len(x[1]))
print(f"{len(dups)} duplicate groups among unmatched units")
for b, members in dups[:14]:
    print(f"\n  {len(members)}x  {members[0][1]} B  {b.hex()[:76]}")
    for va, size in members[:6]:
        print(f"     {va}")
