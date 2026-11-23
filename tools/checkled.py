"""checkled.py - consistency check for the ledger and its sources.

Verifies the things a human forgets:
  * every row parses and has a known status
  * no address appears twice
  * every referenced source file exists
  * every source in src/calib/ is referenced (unreferenced ones belong in src/attic/)

Exit code 0 = consistent. `tools/verify.py` proves the *bytes*; this proves the
*bookkeeping*.
"""
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "docs", "MATCHING.md")
STATUSES = {"MATCH", "RELOCS", "PENDING"}

rows = []
for line in open(LEDGER, encoding="utf-8"):
    m = re.match(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\w+)", line)
    if m:
        rows.append((f"{m.group(1)}:{m.group(2)}", m.group(3), int(m.group(4)), m.group(5)))

problems = []

bad = [r for r in rows if r[3] not in STATUSES]
if bad:
    problems.append(f"{len(bad)} row(s) with unknown status: {bad[:3]}")

dups = {a: c for a, c in Counter(r[0] for r in rows).items() if c > 1}
if dups:
    problems.append(f"duplicate addresses: {dups}")

zero = [r for r in rows if r[2] <= 0]
if zero:
    problems.append(f"{len(zero)} row(s) with size 0: {zero[:3]}")

ledger_text = open(LEDGER, encoding="utf-8").read()
referenced = set(re.findall(r"src=(src/[^;]+)", ledger_text))
missing = sorted(r for r in referenced if not os.path.isfile(os.path.join(ROOT, r)))
if missing:
    problems.append(f"referenced sources missing: {missing}")

calib = {f"src/calib/{f}" for f in os.listdir(os.path.join(ROOT, "src", "calib"))
         if f.endswith(".c")}
orphans = sorted(calib - referenced)
if orphans:
    problems.append(f"{len(orphans)} unattested source(s) in src/calib (move to src/attic): {orphans[:5]}")

counts = Counter(r[3] for r in rows)
print(f"ledger rows: {len(rows)}  "
      f"MATCH {counts.get('MATCH', 0)}, RELOCS {counts.get('RELOCS', 0)}, "
      f"PENDING {counts.get('PENDING', 0)}")
print(f"referenced sources: {len(referenced)}  calib files: {len(calib)}")

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  " + p)
    sys.exit(1)
print("ledger: consistent")
