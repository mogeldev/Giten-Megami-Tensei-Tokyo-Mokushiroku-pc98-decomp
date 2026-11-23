#!/usr/bin/env python3
"""omfdump.py <obj> — OMF reader (template phase 1: OBJ_DUMP, core for match.py).

Supports MSC-7 OMF including the Microsoft extension (COMENT class 0xA2):
fixups appear there as compact 0x9C records (3 bytes per entry:
flags/offset/fixdata) directly after the LEDATA — instead of classic FIXUPP 0xF4.
LOC encoding in the flags byte is identical to the classic (bits 5..2).

API for match.py: load(obj) -> (ledatas, pubdefs)
  ledatas: [{'seg','off','data','fixups':[(off,size)]}]
  pubdefs: {name: (seg, off)}"""
import sys

LOC_SIZE = {0: 1, 1: 2, 2: 2, 3: 4, 4: 1, 5: 4, 9: 2, 10: 4, 11: 2, 13: 4}


def _parse_fixupp_classic(rec):
    out = []
    i = 0
    while i < len(rec):
        b = rec[i]
        if not (b & 0x80):                    # THREAD
            i += 2
            continue
        locat = ((b & 0x7F) << 8) | rec[i + 1]
        loc = (locat >> 10) & 0xF
        off = locat & 0x3FF
        fd = rec[i + 2]
        frame = (fd >> 4) & 0x7
        target = (fd >> 2) & 0x3
        d = fd & 0x1
        i += 3
        if frame in (0, 1, 2):
            i += 1
        elif frame == 3:
            i += 2
        if target in (0, 1, 2):
            i += 1
        if d:
            i += 2
        if loc not in LOC_SIZE:
            raise ValueError(f"unknown LOC type {loc}")
        out.append((off, LOC_SIZE[loc]))
    return out


def _parse_fixups_compact(rec):
    """MSC-7 extension: entries (flags, offset, fixdata[, target index]).
    Observed forms: fd&0x80 -> 3-byte entry (fd=0x9D);
    otherwise 4-byte entry with target index (fd=0x56). Anything not observed aborts."""
    out = []
    i = 0
    while i < len(rec):
        if i + 3 > len(rec):
            raise ValueError("compact FIXUPP: truncated entry")
        flags, off, fd = rec[i], rec[i + 1], rec[i + 2]
        if not (flags & 0x80):
            raise ValueError(f"compact FIXUPP without fixup bit: {flags:#x}")
        loc = (flags >> 2) & 0xF
        if loc not in LOC_SIZE:
            raise ValueError(f"unknown LOC type {loc} (compact)")
        i += 3
        if not (fd & 0x80):          # target-index byte follows
            i += 1
        out.append((off, LOC_SIZE[loc]))
    return out


def load(path):
    data = open(path, "rb").read()
    pos = 0
    ledatas = []
    pubdefs = {}
    while pos + 3 <= len(data):
        rtype = data[pos]
        rlen = data[pos + 1] | (data[pos + 2] << 8)
        if pos + 3 + rlen > len(data):
            raise ValueError(f"record at {pos:#x} runs past end of file")
        rec = data[pos + 3: pos + 3 + rlen - 1]
        if rtype == 0xA0:                                   # LEDATA
            ledatas.append({"seg": rec[0], "off": rec[1] | (rec[2] << 8),
                            "data": rec[3:], "fixups": []})
        elif rtype == 0xF4:                                 # classic FIXUPP
            if not ledatas:
                raise ValueError("FIXUPP without LEDATA")
            ledatas[-1]["fixups"] = _parse_fixupp_classic(rec)
        elif rtype == 0x9C and ledatas:                     # compact FIXUPP (MS A2)
            ledatas[-1]["fixups"] = _parse_fixups_compact(rec)
        elif rtype == 0x90:                                  # PUBDEF
            i = 0
            grp = rec[i]
            i += 1
            if grp == 0 and rec[i] == 0:                     # absolute frame: 2 bytes
                i += 3
            seg = rec[i]
            i += 1
            while i < len(rec) and rec[i] > 0:
                n = rec[i]
                if i + 1 + n + 2 > len(rec):
                    break                      # padding byte/checksum remainder
                name = rec[i + 1: i + 1 + n].decode("latin-1")
                off = rec[i + 1 + n] | (rec[i + 2 + n] << 8)
                pubdefs[name] = (seg, off)
                i += 1 + n + 2
                if i < len(rec) and rec[i] == 0:   # MS debug: type-index byte
                    i += 1
        pos += 3 + rlen
    return ledatas, pubdefs


def main():
    ledatas, pubdefs = load(sys.argv[1])
    print(f"# {len(ledatas)} LEDATA, {len(pubdefs)} PUBDEFs")
    for name, (seg, off) in pubdefs.items():
        print(f"PUB {name}: seg={seg} off={off:#x}")
    for k, ld in enumerate(ledatas, 1):
        print(f"LEDATA {k}: seg={ld['seg']} off={ld['off']:#x} bytes={len(ld['data'])}")
        d = ld["data"]
        for i in range(0, min(len(d), 256), 16):
            print("  " + " ".join(f"{x:02X}" for x in d[i:i + 16]))
        if ld["fixups"]:
            print("  FIXUPPs:", ", ".join(f"off={o} size={s}" for o, s in ld["fixups"]))


if __name__ == "__main__":
    main()
