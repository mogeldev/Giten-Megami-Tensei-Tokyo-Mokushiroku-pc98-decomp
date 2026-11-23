#!/usr/bin/env python3
"""omfdump.py <obj> — OMF-Reader (Vorlage Phase 1: OBJ_DUMP, Kern fuer match.py).

Unterstuetzt MSC-7-OMF inklusive der Microsoft-Erweiterung (COMENT class 0xA2):
Fixups erscheinen dort als kompakte 0x9C-Records (3 Byte je Eintrag:
flags/offset/fixdata) direkt nach dem LEDATA — statt klassischem FIXUPP 0xF4.
LOC-Kodierung im flags-Byte ist identisch zum Klassiker (bits 5..2).

API fuer match.py: load(obj) -> (ledatas, pubdefs)
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
            raise ValueError(f"unbekannter LOC-Typ {loc}")
        out.append((off, LOC_SIZE[loc]))
    return out


def _parse_fixups_compact(rec):
    """MSC-7-Erweiterung: 3-Byte-Eintraege (flags, offset, fixdata)."""
    if len(rec) % 3:
        raise ValueError(f"kompakter FIXUPP-Record ungerade Laenge {len(rec)}")
    out = []
    for i in range(0, len(rec), 3):
        flags, off, _fd = rec[i], rec[i + 1], rec[i + 2]
        if not (flags & 0x80):
            raise ValueError(f"kompakter FIXUPP ohne Fixup-Bit: {flags:#x}")
        loc = (flags >> 2) & 0xF
        if loc not in LOC_SIZE:
            raise ValueError(f"unbekannter LOC-Typ {loc} (kompakt)")
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
            raise ValueError(f"Record bei {pos:#x} laeuft ueber Dateiende")
        rec = data[pos + 3: pos + 3 + rlen - 1]
        if rtype == 0xA0:                                   # LEDATA
            ledatas.append({"seg": rec[0], "off": rec[1] | (rec[2] << 8),
                            "data": rec[3:], "fixups": []})
        elif rtype == 0xF4:                                 # FIXUPP klassisch
            if not ledatas:
                raise ValueError("FIXUPP ohne LEDATA")
            ledatas[-1]["fixups"] = _parse_fixupp_classic(rec)
        elif rtype == 0x9C and ledatas:                     # FIXUPP kompakt (MS A2)
            ledatas[-1]["fixups"] = _parse_fixups_compact(rec)
        elif rtype == 0x90:                                  # PUBDEF
            i = 0
            grp = rec[i]
            i += 1
            if grp == 0 and rec[i] == 0:                     # Frame-Absolut: 2 Byte
                i += 3
            seg = rec[i]
            i += 1
            while i < len(rec) and rec[i] > 0:
                n = rec[i]
                if i + 1 + n + 2 > len(rec):
                    break                      # Fuellbyte/Checksummen-Rest
                name = rec[i + 1: i + 1 + n].decode("latin-1")
                off = rec[i + 1 + n] | (rec[i + 2 + n] << 8)
                pubdefs[name] = (seg, off)
                i += 1 + n + 2
                if i < len(rec) and rec[i] == 0:   # MS-Debug: Typindex-Byte
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
