#!/usr/bin/env python3
"""extract_disks.py - unpack files from the Microsoft C 6.00A floppy images.

The original distribution ships as eight 1.2 MB FAT12 images under
toolchain/msc6_disks, with every file compressed by Microsoft COMPRESS (the
"SZ" + 88 F0 27 variant, header 12 bytes, LZSS with a 4 KB ring buffer).

  python tools/extract_disks.py --list
  python tools/extract_disks.py --out ../toolchain/msc6dos CL.EX$ CL.MS$ CL.ER$ C1.EX$ C2.EX$ C1.ER$ C23.ER$

Mapping used for the DOS toolchain: CL.EX$ -> CL.EXE, CL.MS$ -> CL.MSG,
CL.ER$ -> CL.ERR, C1.EX$ -> C1.EXE, C2.EX$ -> C2.EXE, C1.ER$ -> C1.ERR,
C23.ER$ -> C23.ERR.  Note that DISK2's CL.EX$ is the OS/2 (NE) driver; the DOS
one is on DISK6 (see PACKING.LST: "cl.exe - DOS compiler driver").
"""
import argparse
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISKS = os.path.join(ROOT, "..", "toolchain", "msc6_disks")

PREF = {"CL.EX$": "DISK6.IMG"}   # DISK2 holds the OS/2 (NE) driver
MAP = {"CL.EX$": "CL.EXE", "CL.MS$": "CL.MSG", "CL.ER$": "CL.ERR",
       "C1.EX$": "C1.EXE", "C2.EX$": "C2.EXE", "C1.ER$": "C1.ERR",
       "C23.ER$": "C23.ERR", "C1L.EX$": "C1L.EXE", "C2L.EX$": "C2L.EXE"}


def szdd(data):
    """Decompress a Microsoft COMPRESS stream (SZ .. 88 F0 27 header)."""
    if not (data[:2] == b"SZ" and data[3:6] == b"\x88\xf0\x27"):
        raise ValueError("not a COMPRESS stream: %r" % data[:8])
    size = struct.unpack_from("<I", data, 8)[0]
    p = 12
    out = bytearray()
    ring = bytearray(b" " * 4096)
    pos = 0xFEE
    while len(out) < size:
        flags = data[p]
        p += 1
        for _ in range(8):
            if len(out) >= size:
                break
            if flags & 1:
                c = data[p]
                p += 1
                out.append(c)
                ring[pos] = c
                pos = (pos + 1) & 0xFFF
            else:
                lo, hi = data[p], data[p + 1]
                p += 2
                off = lo | ((hi & 0xF0) << 4)
                ln = (hi & 0x0F) + 3
                for _k in range(ln):
                    c = ring[off]
                    out.append(c)
                    ring[pos] = c
                    off = (off + 1) & 0xFFF
                    pos = (pos + 1) & 0xFFF
                    if len(out) >= size:
                        break
            flags >>= 1
    return bytes(out)


def read_image(path):
    """Return {NAME.EXT: bytes} for a FAT12 floppy image."""
    b = open(path, "rb").read()
    bps = struct.unpack_from("<H", b, 11)[0]
    spc = b[13]
    res = struct.unpack_from("<H", b, 14)[0]
    nfats = b[16]
    rent = struct.unpack_from("<H", b, 17)[0]
    fatsz = struct.unpack_from("<H", b, 22)[0]
    fat_off = res * bps
    root_off = fat_off + nfats * fatsz * bps
    data_off = root_off + (rent * 32 + bps - 1) // bps * bps
    fat = b[fat_off:fat_off + fatsz * bps]
    csize = spc * bps

    def chain(start):
        out = bytearray()
        c = start
        while 2 <= c < 0xFF8:
            out += b[data_off + (c - 2) * csize: data_off + (c - 2) * csize + csize]
            off = c + c // 2
            v = struct.unpack_from("<H", fat, off)[0]
            c = (v >> 4) if (c & 1) else (v & 0x0FFF)
        return bytes(out)

    files = {}
    for i in range(rent):
        e = b[root_off + i * 32: root_off + i * 32 + 32]
        if len(e) < 32 or e[0] == 0:
            break
        if e[0] == 0xE5 or (e[11] & 0x08):
            continue
        name = (e[0:8].decode("latin-1").rstrip() + "." + e[8:11].decode("latin-1").rstrip()).rstrip(".")
        size = struct.unpack_from("<I", e, 28)[0]
        files[name] = chain(struct.unpack_from("<H", e, 26)[0])[:size]
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="files to extract, e.g. CL.EX$")
    ap.add_argument("--out", help="output directory")
    ap.add_argument("--list", action="store_true", help="list image contents")
    a = ap.parse_args()
    images = sorted(os.listdir(DISKS)) if os.path.isdir(DISKS) else []
    if not images:
        sys.exit("no images under %s" % DISKS)
    images.sort(key=lambda n: (0 if PREF.get("CL.EX$") == n else 1, n))
    lists = [(n, read_image(os.path.join(DISKS, n))) for n in images]
    if a.list:
        for n, files in lists:
            print(n, ", ".join(sorted(files)))
        return
    if not a.names or not a.out:
        sys.exit("give file names and --out")
    os.makedirs(a.out, exist_ok=True)
    for want in a.names:
        for n, files in lists:
            if want in files:
                raw = szdd(files[want])
                dst = os.path.join(a.out, MAP.get(want, want.replace("$", "")))
                open(dst, "wb").write(raw)
                print(f"{n}: {want} -> {dst} ({len(raw)} bytes, {raw[:2]!r})")
                break
        else:
            print(f"{want}: not found")


if __name__ == "__main__":
    main()
