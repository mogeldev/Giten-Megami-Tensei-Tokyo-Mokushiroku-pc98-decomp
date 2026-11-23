#!/usr/bin/env python3
"""coverage.py — ehrliche Metrik (Vorlage Phase 6): Bytes pro 64-KiB-Region.

Gezaehlt wird der Anteil der INVENTARISIERTEN Code-Bytes (Summe der
Funktionsgroessen aus ground_truth/functions.csv), die im Ledger als
MATCH/RELOCS verifiziert sind — nicht die Funktionszahl. PENDING zaehlt
separat. Fremd-CRT (Bibliothekssignaturen) und Daten (Fehlinventarisierung)
werden abgezogen und getrennt ausgewiesen.

`compute()` liefert die Zahlen auch an tools/report.py — eine Quelle, zwei
Ausgaben (Konsole und docs/STATUS.md)."""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_BASE = 0x10000


def read_ledger():
    """{linear: (va, name, size, status, note)} aus docs/MATCHING.md."""
    rows = {}
    with open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", line)
            if not m:
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            va, name, size, status = parts[0], parts[1], int(parts[2]), parts[3]
            lin = int(va.split(":")[0], 16) * 16 + int(va.split(":")[1], 16)
            rows[lin] = (va, name, size, status, parts[4] if len(parts) > 4 else "")
    return rows


def compute():
    # Eine Quelle: functions.csv traegt section=CODE|DATA (DATA = belegte
    # Fehlinventarisierung, s. not_code.csv). Nur CODE zaehlt als Funktion.
    funcs, notcode = {}, {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "functions.csv"))):
        lin, size = int(r["linear"], 16), int(r["size"])
        (notcode if r.get("section") == "DATA" else funcs)[lin] = size
    foreign = {}
    fc = os.path.join(ROOT, "ground_truth", "foreign_crt.csv")
    if os.path.isfile(fc):
        for r in csv.DictReader(open(fc)):
            foreign[int(r["linear"], 16)] = int(r["size"])

    ledger = read_ledger()
    matched = {lin: v[2] for lin, v in ledger.items() if v[3] in ("MATCH", "RELOCS")}
    pending = {lin: v[2] for lin, v in ledger.items() if v[3] == "PENDING"}

    regions = {}

    def reg_of(lin):
        return (lin - IMG_BASE) >> 16

    def bucket(reg):
        return regions.setdefault(reg, {"total": 0, "matched": 0, "pend": 0,
                                        "fremd": 0, "notcode": 0, "n": 0, "nm": 0})

    for lin, size in funcs.items():
        d = bucket(reg_of(lin))
        d["total"] += size
        d["n"] += 1
    for lin, size in matched.items():
        d = bucket(reg_of(lin))
        d["matched"] += size
        d["nm"] += 1
    for lin, size in pending.items():
        bucket(reg_of(lin))["pend"] += size
    for lin, size in foreign.items():
        if reg_of(lin) in regions:
            regions[reg_of(lin)]["fremd"] += size
    # regions["total"] zaehlt nur CODE-Rows; Daten/Sondertreiber kommen separat
    # dazu und werden nie als Funktion gezaehlt.
    for lin, size in notcode.items():
        bucket(reg_of(lin))["notcode"] += size

    tot_b = sum(d["total"] for d in regions.values())
    ok_b = sum(d["matched"] for d in regions.values())
    pend_b = sum(d["pend"] for d in regions.values())
    fremd_b = sum(d["fremd"] for d in regions.values())
    nc_b = sum(d["notcode"] for d in regions.values())
    tot_f = sum(d["n"] for d in regions.values())
    ok_f = sum(d["nm"] for d in regions.values())
    eig_b = tot_b - fremd_b

    return {
        "regions": regions,
        "tot_b": tot_b, "ok_b": ok_b, "pend_b": pend_b,
        "fremd_b": fremd_b, "nc_b": nc_b,
        "tot_f": tot_f, "ok_f": ok_f, "eig_b": eig_b,
        "n_match": sum(1 for v in ledger.values() if v[3] == "MATCH"),
        "n_relocs": sum(1 for v in ledger.values() if v[3] == "RELOCS"),
        "n_pending": sum(1 for v in ledger.values() if v[3] == "PENDING"),
        "n_data": len(notcode),
        "ledger": ledger,
    }


def main():
    s = compute()
    regions = s["regions"]
    print(f"{'Region':>8} {'Funktionen':>10} {'davon ok':>8} "
          f"{'Code-Bytes':>11} {'verifiziert':>11} {'Fremd-CRT':>9} {'Daten':>6} {'PENDING':>7}")
    for reg in sorted(regions):
        d = regions[reg]
        eig = d["total"] - d["fremd"]
        pct = f"{100 * d['matched'] / eig:.1f}%" if eig > 0 else "-"
        print(f"  {reg:>#6x} {d['n']:>10} {d['nm']:>8} "
              f"{d['total']:>11} {d['matched']:>11} {d['fremd']:>9} "
              f"{d['notcode']:>6} {d['pend']:>7}  ({pct} Eigenbytes)")
    pct = f"{100 * s['ok_b'] / s['eig_b']:.3f}%" if s["eig_b"] else "-"
    print(f"Gesamt: {s['tot_f']} Code-Funktionen, {s['ok_f']} verifiziert — "
          f"{s['tot_b'] + s['nc_b']} inventarisiert (davon {s['nc_b']} Daten, kein Code), "
          f"{s['tot_b']} Code-Bytes, davon {s['fremd_b']} Fremd-CRT -> {s['eig_b']} Eigenbytes, "
          f"{s['ok_b']} verifiziert ({pct}), {s['pend_b']} PENDING")


if __name__ == "__main__":
    main()
