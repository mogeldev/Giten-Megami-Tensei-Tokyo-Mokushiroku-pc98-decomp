#!/usr/bin/env python3
"""coverage.py — ehrliche Metrik (Vorlage Phase 6): Bytes pro 64-KiB-Region.

Gezaehlt wird der Anteil der INVENTARISIERTEN Code-Bytes (Summe der
Funktionsgroessen aus ground_truth/functions.csv), die im Ledger als
MATCH/RELOCS verifiziert sind — nicht die Funktionszahl. PENDING zaehlt
separat. CRT-Fremdcode-Grenzen stehen noch aus (s. CONVENTIONS Offen)."""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_BASE = 0x10000


def main():
    funcs = {int(r["linear"], 16): int(r["size"])
             for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "functions.csv")))}

    ledger = os.path.join(ROOT, "docs", "MATCHING.md")
    matched, pending = {}, {}
    with open(ledger, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", line)
            if not m:
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            va, size, status = parts[0], int(parts[2]), parts[3]
            lin = int(va.split(":")[0], 16) * 16 + int(va.split(":")[1], 16)
            if status in ("MATCH", "RELOCS"):
                matched[lin] = size
            elif status == "PENDING":
                pending[lin] = size

    regions = {}
    for lin, size in funcs.items():
        reg = (lin - IMG_BASE) >> 16
        d = regions.setdefault(reg, {"total": 0, "matched": 0, "pend": 0, "n": 0, "nm": 0})
        d["total"] += size
        d["n"] += 1
    for lin, size in matched.items():
        reg = (lin - IMG_BASE) >> 16
        regions[reg]["matched"] += size
        regions[reg]["nm"] += 1
    for lin, size in pending.items():
        reg = (lin - IMG_BASE) >> 16
        regions[reg]["pend"] += size

    print(f"{'Region':>8} {'Funktionen':>10} {'davon ok':>8} "
          f"{'Code-Bytes':>11} {'verifiziert':>11} {'PENDING':>7}")
    tot_b = ok_b = pend_b = tot_f = ok_f = 0
    for reg in sorted(regions):
        d = regions[reg]
        tot_b += d["total"]
        ok_b += d["matched"]
        pend_b += d["pend"]
        tot_f += d["n"]
        ok_f += d["nm"]
        pct = f"{100 * d['matched'] / d['total']:.1f}%" if d["total"] else "-"
        print(f"  {reg:>#6x} {d['n']:>10} {d['nm']:>8} "
              f"{d['total']:>11} {d['matched']:>11} {d['pend']:>7}  ({pct} Bytes)")
    pct = f"{100 * ok_b / tot_b:.3f}%" if tot_b else "-"
    print(f"Gesamt: {tot_f} Funktionen, {ok_f} verifiziert — "
          f"{tot_b} Code-Bytes, {ok_b} verifiziert ({pct}), {pend_b} PENDING")


if __name__ == "__main__":
    main()
