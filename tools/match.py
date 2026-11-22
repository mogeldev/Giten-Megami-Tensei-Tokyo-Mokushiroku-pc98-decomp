#!/usr/bin/env python3
"""match.py <va> <symbol> [--size N] -- Byte-Match-Harness (Vorlage Phase 3).

Klassifiziert MATCH (identisch), RELOCS (identisch bis auf Byte-Stellen, fuer die
die Objektdatei Relocations liefert — der erwartete Normalzustand) oder DIFF.
Groesse: Inventar-Abstand zur naechsten Funktion; --size ueberschreibt; 0 verboten.
Bis die MSC-8-Toolchain kalibriert ist, bricht der BUILD-Schritt kontrolliert ab
(TOOLCHAIN_NOT_CALIBRATED) — nichts wird gefaked."""
import argparse
import csv
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compare(orig, mine, relocs):
    """(status, diffs, masked). relocs = Byte-Offsets mit Linker-Operand."""
    diffs, masked = [], 0
    for i in range(min(len(orig), len(mine))):
        if i in relocs:
            masked += 1
            continue
        if orig[i] != mine[i]:
            diffs.append((i, orig[i], mine[i]))
    if len(mine) != len(orig):
        diffs.append((min(len(orig), len(mine)), "LEN", f"{len(orig)} vs {len(mine)}"))
    if not diffs:
        return ("RELOCS" if masked else "MATCH"), diffs, masked
    return "DIFF", diffs, masked


def selftest():
    a = bytes(range(64))
    st, d, m = compare(a, a, set())
    assert st == "MATCH" and not d and m == 0
    b = bytearray(a)
    b[4] ^= 1
    st, d, _ = compare(a, bytes(b), set())
    assert st == "DIFF" and d[0][0] == 4
    st, d, m = compare(a, bytes(b), {4})
    assert st == "RELOCS" and m == 1 and not d
    st, d, m = compare(a, a, {7, 9})
    assert st == "RELOCS" and m == 2
    st, d, m = compare(a, a[:60], set())
    assert st == "DIFF" and d[0][1] == "LEN"
    print("selftest OK: MATCH/RELOCS/DIFF, Reloc-Maskierung, Laengendiff")


def load_funcs():
    path = os.path.join(ROOT, "ground_truth", "functions.csv")
    with open(path) as f:
        return {int(r["linear"], 16): int(r["size"]) for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("va", nargs="?")
    ap.add_argument("symbol", nargs="?")
    ap.add_argument("--size", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    if not a.va or not a.symbol:
        ap.error("va und symbol erforderlich (oder --selftest)")

    va = a.va.strip().lower()
    lin = ((int(va.split(":")[0], 16) << 4) + int(va.split(":")[1], 16)) \
        if ":" in va else int(va, 16)
    funcs = load_funcs()
    size = a.size if a.size else funcs.get(lin, 0)
    if size <= 0:
        sys.exit(f"FEHLER: {va} nicht im Inventar oder Groesse 0 "
                 f"(erst tools/gt.py laufen lassen; Vorlage Phase 6 verbott 0-Byte-Match)")
    print(f"match {va} ({lin:#x}) symbol={a.symbol} size={size}")

    # 1) Build (Cache *.stamp aus Flags+mtime folgt mit der Toolchain)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py")])
    if r.returncode != 0:
        sys.exit("\n-> Phase 0 offen: Toolchain kalibrieren, dann match erneut.")
    # 2) Symbol aus OMF-Objekt: BYTES + RELOC-Tabelle (Adapter folgt mit Toolchain)
    sys.exit("OMF-Adapter (objdump) fehlt noch — folgt mit der kalibrierten Toolchain.")


if __name__ == "__main__":
    main()
