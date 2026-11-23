#!/usr/bin/env python3
"""markcrt.py — CRT-Fremdcode per Bibliothekssignatur in DDS98.EXE markieren
(Vorlage Phase 1: statisch gelinkten Fremdcode getrennt fuehren).

Liest die OMF-Module aus toolchain\\msc7i\\LIB\\MLIBCR.LIB (Microsoft-Librarian:
Module rueck-an-rueck, dann Verzeichnis), nimmt je oeffentlichem Symbol die
Code-Bytes + Reloc-Positionen und sucht sie reloc-maskiert im Load-Image von
DDS98.EXE. Treffer -> ground_truth/foreign_crt.csv (getrennt vom Ledger).

Vorsicht bei winzigen Funktionen: nur Treffer mit eindeutiger Signatur
(mind. MIN_LEN Bytes ausserhalb der Relocs) werden gemeldet."""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import omfdump

LIB = os.path.join(ROOT, "..", "toolchain", "msc7i", "LIB", "MLIBCR.LIB")
BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16
IMG_BASE = 0x10000
IMG_END = 339735
MIN_LEN = 12          # nicht-maskierte Bytes, damit ein Treffer zaehlt


def parse_lib(path):
    """Module aus .LIB: Liste [{'pubs':{name:(seg,off)}, 'ledatas':[...]}]."""
    data = open(path, "rb").read()
    pos = 0
    modules = []
    cur = {"pubs": {}, "ledatas": []}
    while pos + 3 <= len(data):
        rtype = data[pos]
        rlen = data[pos + 1] | (data[pos + 2] << 8)
        if pos + 3 + rlen > len(data):
            break                              # Bibliotheks-Verzeichnis erreicht
        rec = data[pos + 3: pos + 3 + rlen - 1]
        if rtype == 0x80 and cur["pubs"]:     # THEADR = naechstes Modul
            modules.append(cur)
            cur = {"pubs": {}, "ledatas": []}
        if rtype == 0xA0:
            cur["ledatas"].append({"seg": rec[0], "off": rec[1] | (rec[2] << 8),
                                   "data": rec[3:], "fixups": []})
        elif rtype == 0xF4 and cur["ledatas"]:
            cur["ledatas"][-1]["fixups"] = omfdump._parse_fixupp_classic(rec)
        elif rtype == 0x9C and cur["ledatas"]:
            try:
                cur["ledatas"][-1]["fixups"] = omfdump._parse_fixups_compact(rec)
            except ValueError:
                pass
        elif rtype == 0x90:                   # PUBDEF (MSC: Typindex-Byte!)
            i = 0
            grp = rec[i]
            i += 1
            if grp == 0 and rec[i] == 0:
                i += 3
            seg = rec[i]
            i += 1
            while i < len(rec) and rec[i] > 0:
                n = rec[i]
                if i + 1 + n + 2 > len(rec):
                    break
                name = rec[i + 1: i + 1 + n].decode("latin-1")
                off = rec[i + 1 + n] | (rec[i + 2 + n] << 8)
                cur["pubs"][name] = (seg, off)
                i += 1 + n + 2
                if i < len(rec) and rec[i] == 0:
                    i += 1
        elif rtype == 0x8A:                   # MODEND -> Modulende
            modules.append(cur)
            cur = {"pubs": {}, "ledatas": []}
            pos += 3 + rlen
            # MS-Librarian richtet Module aus (Padding bis zur Grenze):
            # zum naechsten THEADR (0x80) vortasten.
            while pos + 3 <= len(data) and data[pos] != 0x80:
                pos += 1
            continue
        pos += 3 + rlen
    if cur["pubs"] or cur["ledatas"]:
        modules.append(cur)
    return modules


def main():
    bin_data = open(BIN, "rb").read()
    code = bin_data[HDR:IMG_END]

    modules = parse_lib(LIB)
    print(f"{LIB}: {len(modules)} Module")

    rows = []
    for mod in modules:
        if not mod["pubs"] or not mod["ledatas"]:
            continue
        for name, (seg, off) in mod["pubs"].items():
            led = next((l for l in mod["ledatas"] if l["seg"] == seg), None)
            if led is None:
                continue
            # Funktionsgroesse: bis zum naechsten PUB im selben Segment
            offs = sorted(o for (s, o) in mod["pubs"].values() if s == seg)
            nxt = min([o for o in offs if o > off], default=off + 32)
            size = min(nxt - off, len(led["data"]) - off)
            if size < MIN_LEN:
                continue
            codeb = led["data"][off: off + size]
            mask = set()
            for (o, s) in led["fixups"]:
                if off <= o < off + size:
                    for k in range(s):
                        if o + k - off < size:
                            mask.add(o + k - off)
            solid = size - len(mask)
            if solid < MIN_LEN:
                continue
            # reloc-maskierte Suche im Load-Image
            hits = []
            for i in range(len(code) - size):
                ok = True
                for j in range(size):
                    if j in mask:
                        continue
                    if code[i + j] != codeb[j]:
                        ok = False
                        break
                if ok:
                    hits.append(i)
            if len(hits) == 1:
                lin = IMG_BASE + hits[0]
                rows.append((f"{lin >> 4:04x}:{lin & 0xF:04x}", hex(lin), name, size))

    rows.sort(key=lambda r: int(r[1], 16))
    out = os.path.join(ROOT, "ground_truth", "foreign_crt.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["va", "linear", "crt_symbol", "size"])
        for r in rows:
            w.writerow(r)
    print(f"{len(rows)} eindeutige CRT-Treffer -> {out}")
    for va, lin, name, size in rows[:20]:
        print(f"  {va}  {name:<24} {size} B")


if __name__ == "__main__":
    main()
