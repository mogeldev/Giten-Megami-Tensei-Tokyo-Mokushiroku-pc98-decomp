#!/usr/bin/env python3
"""disasm.py <seg:off|linear> [n] [--raw] — Hexdump sofort, Instruktionen via Ghidra.

n = Bytes im Hexdump bzw. Anzahl Instruktionen im Ghidra-Teil (Standard 32).
--raw: nur Hexdump, kein (langsamer) Ghidra-Headless-Aufruf."""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ghidra_run  # noqa: E402

BIN = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
HDR = 896 * 16
IMG_BASE = 0x10000


def parse_va(va):
    va = va.strip().lower()
    if ":" in va:
        s, o = va.split(":")
        s, o = int(s, 16), int(o, 16)
        return s, o, (s << 4) + o
    lin = int(va, 16)
    return lin >> 4, lin & 0xF, lin


def hexdump(data, seg, off):
    # Behalte das eingegebene seg:off als Anzeigeformat; Off wrappt bei 0x10000
    # (Real Mode). Intern gerechnet wird ueberall linear.
    for i in range(0, len(data), 16):
        c = data[i:i + 16]
        print(f"{seg:04x}:{(off + i) & 0xFFFF:04x}  "
              + " ".join(f"{x:02x}" for x in c).ljust(47)
              + "  " + "".join(chr(x) if 32 <= x < 127 else "." for x in c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("va")
    ap.add_argument("n", nargs="?", type=int, default=32)
    ap.add_argument("--raw", action="store_true")
    a = ap.parse_args()
    seg, off, lin = parse_va(a.va)

    data = open(BIN, "rb").read()[lin - IMG_BASE + HDR: lin - IMG_BASE + HDR + a.n]
    if not data:
        sys.exit("FEHLER: Adresse ausserhalb des Load-Images")
    hexdump(data, seg, off)
    if a.raw:
        return

    log = os.path.join(ROOT, "tools", ".disasm.log")
    rc = ghidra_run.run("DDS98.EXE",
                        ["-postScript", "DisasmRange.java",
                         f"{seg:04x}:{off:04x}", str(a.n)], log)
    found = 0
    with open(log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("DIS\t"):
                _, addr, hexb, ins = line.rstrip("\n").split("\t", 3)
                print(f"{addr}  {hexb:18}  {ins}")
                found += 1
    if rc != 0 or found == 0:
        print(f"(Ghidra rc={rc}, Instruktionen={found}; Log-Tail:)", file=sys.stderr)
        with open(log, encoding="utf-8", errors="replace") as fh:
            print("".join(fh.readlines()[-12:]), file=sys.stderr)


if __name__ == "__main__":
    main()
