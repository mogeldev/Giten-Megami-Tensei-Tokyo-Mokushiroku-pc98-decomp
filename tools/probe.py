#!/usr/bin/env python3
"""probe.py - sweep every calibration probe object over every unmatched unit.

Each `src/calib/*.c` object contains symbols that are byte-exact for some shape.
Any unmatched image unit of the same length that matches the symbol's bytes
(modulo call targets) is a legitimate new row - the same source and symbol
reproduce it. This generalises tools/reuse.py from "same size as a ledger row"
to "same size as any probe symbol", and runs entirely in-process before it
confirms hits with match.py.
"""
import argparse
import csv
import glob
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]

spec = importlib.util.spec_from_file_location("omfdump", os.path.join(ROOT, "tools", "omfdump.py"))
omf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(omf)

ROW = re.compile(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|")


def linear(va):
    s, o = va.split(":")
    return int(s, 16) * 16 + int(o, 16)


def norm(b):
    out = bytearray(b)
    i = 0
    while i < len(out) - 1:
        if out[i:i + 3] == b"\x90\x0e\xe8":
            out[i + 3:i + 5] = b"\x00\x00"
            i += 5
            continue
        if out[i:i + 2] == b"\x1e\x68":          # push ds; push <DGROUP disp16>
            out[i + 2:i + 4] = b"\x00\x00"
            i += 4
            continue
        if out[i] == 0x9A:
            out[i + 1:i + 5] = b"\x00\x00\x00\x00"
            i += 5
            continue
        if out[i] == 0xE8 and i + 2 < len(out):
            out[i + 1:i + 3] = b"\x00\x00"
            i += 3
            continue
        i += 1
    return bytes(out)


def ledger_rows():
    """Map va -> (name, src, flags, msc, nodpmi) for verified rows."""
    out = {}
    for line in open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8"):
        m = ROW.match(line.strip())
        if not m:
            continue
        body = line.strip()
        cols = [c.strip() for c in body.strip("|").split("|")]
        if len(cols) < 5 or cols[3] not in ("MATCH", "RELOCS"):
            continue
        note = cols[4]
        src = re.search(r"src=(\S+);", note)
        flags = re.search(r'flags="([^"]*)"', note)
        if not src or not flags:
            continue
        msc = re.search(r"\bmsc=(\w+)", note)
        out[f"{m.group(1)}:{m.group(2)}"] = (cols[1], src.group(1), flags.group(1),
                                             msc.group(1) if msc else "", "nodpmi" in note)
    return out


def symbols(obj):
    """(name, pattern) for every public symbol.

    The pattern masks every FIXUPP site (2 or 4 bytes), so two instances of the
    same shape that differ only in their relocated operands - call targets,
    global addresses, DGROUP pointers - compare equal. match.py still confirms
    every hit, so a wildcard can never produce a false row.
    """
    try:
        ledatas, pubdefs = omf.load(obj)
    except Exception:
        return []
    data = b"".join(ld["data"] for ld in ledatas if ld["seg"] == 1)
    base = min((ld["off"] for ld in ledatas if ld["seg"] == 1), default=0)
    fix = []
    for ld in ledatas:
        if ld["seg"] != 1:
            continue
        for (foff, fsize) in ld.get("fixups", []):
            fix.append((ld["off"] + foff - base, fsize))
    offs = sorted({off - base for (seg, off) in pubdefs.values() if seg == 1})
    out = []
    for name, (seg, off) in pubdefs.items():
        if seg != 1:
            continue
        o = off - base
        nxt = [x for x in offs if x > o]
        end = nxt[0] if nxt else len(data)
        body = list(data[o:end])
        while body and body[-1] == 0x90:
            body.pop()
        for (foff, fsize) in fix:
            for k in range(foff, min(foff + fsize, o + len(body))):
                if k >= o:
                    body[k - o] = None
        if body:
            out.append((name, bytes([0 if b is None else b for b in body]), len(body),
                        frozenset(i for i, b in enumerate(body) if b is None)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=80)
    a = ap.parse_args()

    known = ledger_rows()
    seen = {linear(v) for v in known}

    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        lin = int(r["linear"], 16)
        units.setdefault(lin, (r["va"], int(r["size"])))

    # build the probe library: (src, flags, msc, nodpmi, name, normbytes, size)
    lib = []
    for src in sorted(glob.glob(os.path.join(ROOT, "src", "calib", "*.c"))):
        # inline-assembly probes are ASM rows, not C coverage - never claim them here
        if "__asm" in open(src, encoding="utf-8", errors="replace").read():
            continue
        flags, msc, nodpmi = "/G1 /AM /Gs /Os", "", False
        # reuse the flags recorded for this source in the ledger, if any
        for name, s, f, m, nd in known.values():
            if s == os.path.relpath(src, ROOT).replace("\\", "/") or s == src:
                flags, msc, nodpmi = f, m, nd
                break
        obj = os.path.join(ROOT, "build", os.path.splitext(os.path.basename(src))[0] + ".OBJ")
        if not os.path.exists(obj):
            continue
        for name, pat, n, wild in symbols(obj):
            lib.append((os.path.relpath(src, ROOT).replace("\\", "/"), flags, msc, nodpmi,
                        name, pat, n, wild))

    lib.sort(key=lambda x: -x[6])
    hits = []
    for lin, (va, size) in sorted(units.items(), key=lambda kv: -kv[1][1]):
        if lin in seen:
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size]
        nb = b.rstrip(b"\x90")
        for src, flags, msc, nodpmi, name, pat, n, wild in lib:
            if n > len(nb):
                continue
            # a symbol may also be a prefix of the unit (trailing padding)
            ok = True
            for i in range(n):
                if i not in wild and pat[i] != nb[i]:
                    ok = False
                    break
            if not ok:
                continue
            hits.append((va, n, name, src, flags, msc, nodpmi))
            seen.add(lin)
            break
        if len(hits) >= a.limit:
            break

    print(f"# {len(hits)} pattern hits (confirming with match.py)")
    good = []
    for va, size, name, src, flags, msc, nodpmi in hits:
        cmd = [PY, os.path.join(ROOT, "build.py"), src, "--flags", flags, "--force"]
        if msc:
            cmd += ["--msc-dir", msc]
        if nodpmi:
            cmd += ["--no-dpmi"]
        subprocess.run(cmd, capture_output=True, text=True)
        obj = os.path.join(ROOT, "build", os.path.splitext(os.path.basename(src))[0] + ".OBJ")
        q = subprocess.run([PY, os.path.join(ROOT, "tools", "match.py"), va, name,
                            "--obj", obj, "--size", str(size)], capture_output=True, text=True)
        out = (q.stdout or "").strip().splitlines()
        if out and ("RELOCS" in out[0] or "MATCH" in out[0]):
            status = "MATCH" if "MATCH" in out[0] else "RELOCS"
            good.append((va, size, name, src, flags, msc, nodpmi, status))
            print(f"  {va} = {name} ({src}, {size} B, {status})")
        else:
            print(f"  {va}: diff ({out[0] if out else '?'})")

    if a.write and good:
        p = os.path.join(ROOT, "docs", "MATCHING.md")
        text = open(p, encoding="utf-8").read().rstrip("\n")
        add = []
        for va, size, name, src, flags, msc, nodpmi, status in good:
            note = f"src={src}; flags=\"{flags}\";"
            if msc:
                note += f" msc={msc};"
            if nodpmi:
                note += " nodpmi;"
            note += " reuses a calibration probe shape (confirmed by match.py)"
            add.append(f"| {va} | {name} | {size} | {status} | {note} |")
        open(p, "w", encoding="utf-8", newline="\n").write(text + "\n" + "\n".join(add) + "\n")
        print(f"# appended {len(add)} rows")


if __name__ == "__main__":
    main()
