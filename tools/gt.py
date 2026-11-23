#!/usr/bin/env python3
"""gt.py — Ground-Truth-Inventar aus DDS98.EXE (Vorlage Phase 1).

Erzeugt ground_truth/functions.csv (va, linear, name, size, section),
strings.csv (ASCII im Load-Image), imports.csv (MZ-Notiz: keine Importtabelle).
Groessen werden auf den Abstand zur naechsten Funktion geklemmt; Groesse 0 ist
verboten (Vorlage Phase 6). Self-Checks als asserts."""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dds98/
BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
FUNCS_TXT = os.path.join(ROOT, "..", "decompiled", "DDS98_functions.txt")
HDR = 896 * 16          # MZ-Headergroesse (Dateioffset des Load-Images)
IMG_BASE = 0x10000      # Ghidra-Abbildung: Segment 0x1000:0000
IMG_END = 339735        # Load-Image endet bei diesem Dateioffset
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
    assert rows, "keine Funktionen im Export gefunden"
    assert all(r["size"] > 0 for r in rows), "Funktion mit Groesse 0"
    return rows


def main():
    gt = os.path.join(ROOT, "ground_truth")
    os.makedirs(gt, exist_ok=True)

    rows = load_functions()
    lins = [r["linear"] for r in rows]
    assert lins == sorted(lins) and len(set(lins)) == len(lins), \
        "Adressen nicht streng geordnet/eindeutig"

    # Nicht-Code-Eintraege (Sondertreiber-Befehlsbloecke, Tabellen, Nullfelder,
    # Strings) werden als section=DATA markiert statt geloescht: ihre Groesse
    # haengt am Abstand zur naechsten Funktion, die Zeile traegt also Information.
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
        # va linear als Primaerschluessel (Ghidra seg:off-Splits sind fuer freie
        # Adressen nicht reproduzierbar; functions.csv traegt beide Spalten)
        w.writerow(["va_linear", "text"])
        for m in re.finditer(rb"[\x20-\x7e]{6,}", data[HDR:IMG_END]):
            va = IMG_BASE + m.start()
            w.writerow([hex(va), m.group().decode("ascii")])
            n_str += 1

    with open(os.path.join(gt, "imports.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "ref", "note"])
        w.writerow(["NOTE", "", "MZ hat keine Importtabelle; DOS-Zugriffe laufen ueber INT (21h etc.)"])
        w.writerow(["RTL", "", "MS-C-8-CRT (Banner 1992 in der Binary) als Fremdcode markieren, sobald Region per Kalibrierung identifiziert"])

    n_code = sum(1 for r in rows if r["linear"] not in notcode)
    n_data = len(rows) - n_code
    print(f"functions.csv: {len(rows)} Eintraege = {n_code} Code + {n_data} Daten, "
          f"{sum(r['size'] for r in rows)} Bytes Spanne")
    print(f"strings.csv:   {n_str} ASCII-Strings")
    print("imports.csv:   MZ-Notiz (keine Importtabelle)")


if __name__ == "__main__":
    main()
