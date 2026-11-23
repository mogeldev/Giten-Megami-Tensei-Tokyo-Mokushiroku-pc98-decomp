#!/usr/bin/env python3
"""verify.py — prueft ALLE MATCHING.md-Zeilen erneut; bricht bei Regression ab
(Vorlage Phase 6).

Integritaet: fuer jede (src, flags)-Kombination wird die Quelle mit `build.py`
**neu kompiliert** und danach jede zugehoerige Ledger-Zeile gegen die Original-
Bytes geprueft. Damit haengt das Ergebnis nicht davon ab, welches OBJ gerade in
`build/` liegt (Lehre aus Runde 23). `--fast` ueberspringt den Neubau (nur fuer
schnelle Zwischenchecks, nicht fuer den Close-out).

Groesse kommt aus der Ledger-Spalte (echte Laenge), nicht aus dem Inventar.
Zaehler werden aus dem Ledger neu berechnet, nie aus dem Gedaechtnis."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
BUILD = os.path.join(ROOT, "build")
NOTE_RE = re.compile(r'src=(\S+);\s*flags="([^"]*)"')


def parse_ledger():
    rows, bad = [], []
    with open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8") as f:
        for line in f:
            if not re.match(r"^\|\s*[0-9a-f]{4}:[0-9a-f]{4}\s*\|", line):
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 5:
                bad.append(f"unvollstaendige Zeile: {line.strip()[:80]}")
                continue
            rows.append({"va": parts[0], "name": parts[1], "size": parts[2],
                         "status": parts[3], "note": parts[4]})
    return rows, bad


def main():
    fast = "--fast" in sys.argv
    rows, fails = parse_ledger()

    # Duplikate (Linearadresse) und Groesse 0 sind verboten (Vorlage Phase 6)
    seen = set()
    for r in rows:
        seg, off = r["va"].split(":")
        lin = int(seg, 16) * 16 + int(off, 16)
        if lin in seen:
            fails.append(f"DUP {r['va']}")
        seen.add(lin)
        if int(r["size"]) == 0:
            fails.append(f"GROESSE-0 {r['va']} (0 Bytes vergleichen matcht immer)")

    # Nach (src, flags) gruppieren; je Kombination einmal bauen
    groups = {}
    for r in rows:
        if r["status"] == "PENDING":
            continue
        m = NOTE_RE.search(r["note"])
        if not m:
            fails.append(f"{r['va']}: MATCH/RELOCS ohne src=/flags= in der Notiz")
            continue
        groups.setdefault(m.groups(), []).append(r)

    objs = {}
    for (src, flags), items in groups.items():
        stem = os.path.splitext(os.path.basename(src))[0]
        obj = os.path.join(BUILD, f"{stem}.OBJ")
        if not fast:
            print(f"build {src} [{flags}] ...", flush=True)
            r = subprocess.run([PY, os.path.join(ROOT, "build.py"), src,
                                "--flags", flags],
                               capture_output=True, text=True)
            if r.returncode != 0:
                fails.append(f"BUILD FEHLGESCHLAGEN {src} [{flags}]\n"
                             f"{(r.stdout or '')[-400:]}{(r.stderr or '')[-400:]}")
                continue
        objs[(src, flags)] = obj

    n_match = n_relocs = n_pending = 0
    for r in rows:
        if r["status"] == "PENDING":
            n_pending += 1
            continue
        m = NOTE_RE.search(r["note"])
        obj = objs.get(m.groups()) if m else None
        if not obj:
            continue
        cmd = [PY, os.path.join(ROOT, "tools", "match.py"), r["va"], r["name"],
               "--obj", obj, "--size", r["size"]]
        q = subprocess.run(cmd, capture_output=True, text=True)
        out = ((q.stdout or "") + (q.stderr or "")).strip()
        if q.returncode != 0:
            fails.append(f"{r['va']} {r['name']}: REGRESSION\n{out[:500]}")
            print(f"  {r['va']} {r['name']}: FEHLER")
        else:
            if r["status"] == "MATCH":
                n_match += 1
            else:
                n_relocs += 1
            print(f"  {r['va']} {r['name']}: {r['status']} ok")

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
