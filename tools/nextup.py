#!/usr/bin/env python3
"""nextup.py - rank the remaining unmatched units by how likely they are to match.

The many ad-hoc scans used in earlier rounds are replaced by this single tool. It
applies the same filters every time:

1. skip anything already claimed, CRT code, or not ending at a return;
2. skip fragments (no function prologue) - those can never be matched;
3. skip units whose bytes contain any trait from tools/classify.py, because those
   are blocked by code generation the available compiler does not produce;
4. score the rest: straight-line bodies with several translated calls are the
   easiest to transcribe, so they rank first.

Usage: python tools/nextup.py [--limit N] [--min B] [--max B]
"""
import argparse
import csv
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
ROW = re.compile(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", re.M)

spec = importlib.util.spec_from_file_location("classify", os.path.join(ROOT, "tools", "classify.py"))
classify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--min", type=int, default=12)
    ap.add_argument("--max", type=int, default=120)
    a = ap.parse_args()

    led = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    done = {int(m.group(1), 16) * 16 + int(m.group(2), 16) for m in ROW.finditer(led)}
    crt = {int(r["linear"], 16) for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "foreign_crt.csv")))}

    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))

    out = []
    for lin, (va, size) in units.items():
        if lin in done or lin in crt or not (a.min <= size <= a.max):
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size]
        core = b.rstrip(b"\x90")
        if not core or not (core[-1] in (0xC3, 0xCB) or (len(core) >= 3 and core[-3] in (0xCA, 0xC2))):
            continue
        if not (core[:3] == b"\x55\x8b\xec" or core[:1] == b"\xc8"):
            continue                                    # fragment
        if any(pred(core) for _label, pred, _note in classify.TRAITS):
            continue                                    # blocked trait
        calls = core.count(b"\x90\x0e\xe8")
        branches = sum(core.count(bytes([x])) for x in (0x74, 0x75, 0x7C, 0x7D, 0xE2))
        score = calls * 3 - branches
        out.append((score, len(core), va, core.hex(), calls, branches))

    out.sort(reverse=True)
    print(f"# {len(out)} candidate units with no known blocker (best {a.limit} shown)")
    for score, ln, va, hx, calls, branches in out[:a.limit]:
        print(f"{va}\t{ln:>3} B  calls={calls} branches={branches} score={score}")
        print(f"    {hx}")


if __name__ == "__main__":
    main()
