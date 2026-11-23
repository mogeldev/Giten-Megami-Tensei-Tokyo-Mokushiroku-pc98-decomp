#!/usr/bin/env python3
"""gt.py — ground-truth inventory from DDS98.EXE (template phase 1).

Creates ground_truth/functions.csv (va, linear, name, size, section),
strings.csv (ASCII in the load image), imports.csv (MZ note: no import table).
Sizes are clamped to the distance to the next function; size 0 is
forbidden (template phase 6). Self-checks as asserts."""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dds98/
BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
FUNCS_TXT = os.path.join(ROOT, "..", "decompiled", "DDS98_functions.txt")
HDR = 896 * 16          # MZ header size (file offset of the load image)
IMG_BASE = 0x10000      # Ghidra mapping: segment 0x1000:0000
IMG_END = 339735        # load image ends at this file offset
LINE_RE = re.compile(r"^([0-9a-f]{4}):([0-9a-f]{4})\s+(\S.*)$")


def va_str(lin):
    return f"{lin >> 4:04x}:{lin & 0xF:04x}"


def load_functions():
    rows = []
    with open(FUNCS_TXT, encoding="ascii") as f:
        for line in f:
            m = LINE_RE.match(line.strip())
            if not m:
                continue
            seg, off, name = m.groups()
            rows.append({"linear": (int(seg, 16) << 4) + int(off, 16),
                         "name": name.strip()})
    rows.sort(key=lambda r: r["linear"])
    for i, r in enumerate(rows):
        r["size"] = rows[i + 1]["linear"] - r["linear"] if i + 1 < len(rows) else 16
    assert rows, "no functions found in export"
    assert all(r["size"] > 0 for r in rows), "function with size 0"
    return rows


def main():
    gt = os.path.join(ROOT, "ground_truth")
    os.makedirs(gt, exist_ok=True)

    rows = load_functions()
    lins = [r["linear"] for r in rows]
    assert lins == sorted(lins) and len(set(lins)) == len(lins), \
        "addresses not strictly ordered/unique"

    # Non-code entries (special-driver command blocks, tables, null fields,
    # strings) are marked section=DATA instead of deleted: their size
    # depends on the distance to the next function, so the row carries information.
    notcode = set()
    nc_path = os.path.join(gt, "not_code.csv")
    if os.path.isfile(nc_path):
        with open(nc_path) as f:
            for r in csv.DictReader(f):
                notcode.add(int(r["linear"], 16))

    with open(os.path.join(gt, "functions.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["va", "linear", "name", "size", "section"])
        for r in rows:
            w.writerow([va_str(r["linear"]), hex(r["linear"]), r["name"],
                        r["size"], "DATA" if r["linear"] in notcode else "CODE"])

    data = open(BIN, "rb").read()
    n_str = 0
    with open(os.path.join(gt, "strings.csv"), "w", newline="") as f:
        w = csv.writer(f)
        # va linear as primary key (Ghidra seg:off splits are not reproducible
        # for free addresses; functions.csv carries both columns)
        w.writerow(["va_linear", "text"])
        for m in re.finditer(rb"[\x20-\x7e]{6,}", data[HDR:IMG_END]):
            va = IMG_BASE + m.start()
            w.writerow([hex(va), m.group().decode("ascii")])
            n_str += 1

    with open(os.path.join(gt, "imports.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "ref", "note"])
        w.writerow(["NOTE", "", "MZ has no import table; DOS accesses go through INT (21h etc.)"])
        w.writerow(["RTL", "", "Mark MS-C-8 CRT (1992 banner in the binary) as foreign code once the region is identified by calibration"])

    n_code = sum(1 for r in rows if r["linear"] not in notcode)
    n_data = len(rows) - n_code
    print(f"functions.csv: {len(rows)} entries = {n_code} code + {n_data} data, "
          f"{sum(r['size'] for r in rows)} bytes span")
    print(f"strings.csv:   {n_str} ASCII strings")
    print("imports.csv:   MZ note (no import table)")


if __name__ == "__main__":
    main()
