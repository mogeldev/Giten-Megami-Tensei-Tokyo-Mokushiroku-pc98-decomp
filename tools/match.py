#!/usr/bin/env python3
"""match.py <va> <symbol> --obj <datei> [--size N] — Byte-Match-Harness (Vorlage Phase 3).

Vergleicht ein Symbol aus einem MSC-7-OMF-Objekt gegen die Original-Bytes von
DDS98.EXE und klassifiziert:
  MATCH  = identisch
  RELOCS = identisch bis auf Byte-Stellen mit OMF-Fixup (Linker-Operanden)
  DIFF   = Byte-Diffs mit Original- und Eigen-Instruktion
Groesse: Inventar-Abstand zur naechsten Funktion; --size ueberschreibt; 0 verboten.
Fixups werden aus dem Objekt gelesen (MSC-7-kompakte 0x9C-Records, s. omfdump.py)
und nie geraten. Ohne --obj: Abbruch mit Hinweis auf build.py (Layout-Konvention
folgt, sobald echte Subsystem-Quelldateien stehen)."""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import omfdump  # noqa: E402

BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16          # MZ-Headergroesse (Dateioffset des Load-Images)
IMG_BASE = 0x10000      # Ghidra-Abbildung: Segment 0x1000:0000


def linear(va):
    va = va.strip().lower()
    if ":" in va:
        s, o = va.split(":")
        return (int(s, 16) << 4) + int(o, 16)
    return int(va, 16)


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
    with open(os.path.join(ROOT, "ground_truth", "functions.csv")) as f:
        return {int(r["linear"], 16): int(r["size"]) for r in csv.DictReader(f)}


def binary_bytes(lin, size):
    data = open(BIN, "rb").read()
    off = lin - IMG_BASE + HDR
    if off < 0 or off + size > 339735:
        sys.exit(f"FEHLER: {lin:#x} ausserhalb des Load-Images")
    return data[off: off + size]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("va", nargs="?")
    ap.add_argument("symbol", nargs="?")
    ap.add_argument("--obj")
    ap.add_argument("--size", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    if not a.va or not a.symbol or not a.obj:
        ap.error("va, symbol und --obj erforderlich (oder --selftest)")

    lin = linear(a.va)
    funcs = load_funcs()
    size = a.size if a.size else funcs.get(lin, 0)
    if size <= 0:
        sys.exit(f"FEHLER: {a.va} nicht im Inventar oder Groesse 0 — "
                 "erst tools/gt.py laufen lassen; 0-Byte-Match ist verboten")

    ledatas, pubdefs = omfdump.load(a.obj)
    sym = a.symbol if a.symbol in pubdefs else "_" + a.symbol
    if sym not in pubdefs:
        sys.exit(f"FEHLER: Symbol '{a.symbol}' nicht im Objekt "
                 f"(vorhanden: {', '.join(sorted(pubdefs))})")
    seg, off = pubdefs[sym]
    led = next((l for l in ledatas if l["seg"] == seg), None)
    if led is None:
        sys.exit(f"FEHLER: kein LEDATA fuer Segment {seg}")
    code = led["data"][off: off + size]
    if len(code) < size:
        sys.exit(f"FEHLER: Symbol am LEDATA-Ende — size {size} zu gross")
    relocs = {(o + k) - off for (o, s) in led["fixups"]
              if off <= o < off + size for k in range(s)}

    orig = binary_bytes(lin, size)
    status, diffs, masked = compare(orig, code, relocs)
    print(f"{a.va} {a.symbol}: {status}  (size={size}, reloc-maskiert={masked})")
    for (o, ob, mb) in diffs[:12]:
        if isinstance(ob, int):
            print(f"  DIFF @+{o:#x}: orig {ob:02X} vs objekt {mb:02X}")
        else:
            print(f"  DIFF @+{o:#x}: {ob} {mb}")
    sys.exit(0 if status in ("MATCH", "RELOCS") else 1)


if __name__ == "__main__":
    main()
