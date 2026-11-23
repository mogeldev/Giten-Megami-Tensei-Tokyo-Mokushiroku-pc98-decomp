#!/usr/bin/env python3
"""verify.py — prueft ALLE MATCHING.md-Zeilen erneut; bricht bei Regression ab
(Vorlage Phase 6). Zaehler werden aus dem Ledger neu berechnet.
PENDING-Zeilen werden nur gezaehlt; MATCH/RELOCS werden byteweise neu geprueft."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def main():
    ledger = os.path.join(ROOT, "docs", "MATCHING.md")
    rows = []
    with open(ledger, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*([0-9a-f]{4}:[0-9a-f]{4})\s*\|", line)
            if not m:
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 5:
                sys.exit(f"FEHLER: Ledger-Zeile unvollstaendig: {line!r}")
            rows.append(parts[:5])

    seen = set()
    n_match = n_relocs = n_pending = 0
    fails = []
    for va, name, size, status, note in rows:
        lin = int(va.split(":")[0], 16) * 16 + int(va.split(":")[1], 16)
        if lin in seen:
            fails.append(f"DUP {va}")
            continue
        seen.add(lin)
        if int(size) == 0:
            fails.append(f"GROESSE-0 {va} (verboten)")
            continue
        if status == "PENDING":
            n_pending += 1
            continue
        mo = re.search(r"obj=([\w./\\-]+)", note)
        if not mo:
            fails.append(f"{va}: MATCH/RELOCS ohne obj= im Ledger")
            continue
        r = subprocess.run(
            [PY, os.path.join(ROOT, "tools", "match.py"), va, name,
             "--obj", os.path.join(ROOT, mo.group(1))],
            capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0:
            fails.append(f"{va} {name}: REGRESSION\n{out.strip()[:400]}")
        elif status == "MATCH":
            n_match += 1
        elif status == "RELOCS":
            n_relocs += 1
        print(f"  {va} {name}: {status} ok" if r.returncode == 0
              else f"  {va} {name}: FEHLER")

    print(f"Ledger: {len(rows)} Zeilen — MATCH {n_match}, RELOCS {n_relocs}, "
          f"PENDING {n_pending}")
    if fails:
        print("FEHLER:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("verify: gruen")


if __name__ == "__main__":
    main()
