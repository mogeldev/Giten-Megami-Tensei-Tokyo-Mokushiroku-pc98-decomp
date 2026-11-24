#!/usr/bin/env python3
"""oldsweep.py <MSCDIR> [--flags F ...] - rebuild every calibration source under another
compiler and look for unmatched units it now reproduces.

Why not probe.py: probe.py reuses the objects built with MSC 7.0. This tool recompiles each
`src/calib/*.c` and each `src/pending/*.c` with the given toolchain (default MSC51U or MSC6C),
so a compiler that emits different bytes for the same source can turn an unmatched unit into a
match. Sources are rewritten for old compilers first (`__far` -> `far` etc.; MSC 6.0 and 5.1
do not parse the double-underscore spellings, and fail silently with no object).

For every symbol it then tries (a) every unmatched unit of the same length and (b) every
return-bounded prefix/slice of larger units, comparing with relocation fixups masked. A hit is
only a *candidate*: it must still pass `tools/match.py` and `tools/verify.py` before it becomes
a ledger row. Nothing is written to the ledger.

Usage:  python tools/oldsweep.py MSC51U --flags "/AM /G1 /Gs /Os" --flags "/AM /G0 /Gs /Os"
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
WORK = os.path.join(ROOT, "build", "oldsweep")

spec = importlib.util.spec_from_file_location("probe", os.path.join(ROOT, "tools", "probe.py"))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

REWRITE = [("__far", "far"), ("__near", "near"), ("__pascal", "pascal"), ("__cdecl", "cdecl")]


def old_source(text):
    for a, b in REWRITE:
        text = text.replace(a, b)
    return text


def usable(text):
    # constructs the 1988-92 compilers cannot take
    return not re.search(r"__asm|__fastcall|__interrupt|#include|//", text)


def compile_one(src_text, stem, msc, flags):
    os.makedirs(WORK, exist_ok=True)
    rel = os.path.join("build", "oldsweep", stem + ".c")
    with open(os.path.join(ROOT, rel), "w", encoding="ascii", errors="replace") as f:
        f.write(src_text)
    obj = os.path.join(WORK, stem.upper() + ".OBJ")
    if os.path.exists(obj):
        os.remove(obj)
    cmd = [PY, os.path.join(ROOT, "build.py"), rel.replace("\\", "/"), "--msc-dir", msc,
           "--no-dpmi", "--flags", flags, "--force"]
    subprocess.run(cmd, capture_output=True, text=True)
    # build.py writes next to the build dir, not the sub-folder
    alt = os.path.join(ROOT, "build", stem.upper() + ".OBJ")
    if os.path.exists(alt):
        os.replace(alt, obj)
    return obj if os.path.exists(obj) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("msc")
    ap.add_argument("--flags", action="append")
    ap.add_argument("--limit", type=int, default=0, help="stop after N sources (0 = all)")
    a = ap.parse_args()
    flagsets = a.flags or ["/AM /G1 /Gs /Os"]

    known = probe.ledger_rows()
    seen = {probe.linear(v) for v in known}
    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))
    crt = {int(r["linear"], 16) for r in csv.DictReader(
        open(os.path.join(ROOT, "ground_truth", "foreign_crt.csv")))}

    srcs = sorted(glob.glob(os.path.join(ROOT, "src", "calib", "*.c")) +
                  glob.glob(os.path.join(ROOT, "src", "pending", "*.c")))
    if a.limit:
        srcs = srcs[:a.limit]

    lib = []          # (src, flags, name, pattern, size, wildcard-index-set)
    built = skipped = failed = 0
    for src in srcs:
        text = open(src, encoding="utf-8", errors="replace").read()
        if not usable(text):
            skipped += 1
            continue
        stem = "o" + os.path.splitext(os.path.basename(src))[0][:7]
        for fl in flagsets:
            obj = compile_one(old_source(text), stem, a.msc, fl)
            if not obj:
                failed += 1
                continue
            built += 1
            for name, pat, n, wild in probe.symbols(obj):
                lib.append((os.path.relpath(src, ROOT).replace("\\", "/"), fl, name, pat, n, wild))
    print(f"# {a.msc}: built {built} objects ({skipped} sources unusable, {failed} failed), "
          f"{len(lib)} symbols", flush=True)

    by_len = {}
    for e in lib:
        by_len.setdefault(e[4], []).append(e)

    def equal(pat, wild, n, b):
        return all(i in wild or pat[i] == b[i] for i in range(n))

    def ret_ends(b):
        ends = set()
        for i in range(len(b)):
            if b[i] in (0xC3, 0xCB):
                ends.add(i + 1)
            elif b[i] in (0xCA, 0xC2) and i + 2 < len(b):
                ends.add(i + 3)
        return sorted(ends)

    hits = []
    claimed = set()
    for lin, (va, size) in sorted(units.items(), key=lambda kv: -kv[1][1]):
        if lin in seen or lin in crt:
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size]
        nb = b.rstrip(b"\x90")
        ends = ret_ends(b)
        for start in [0] + ends:
            for end in (ends + [len(nb)]):
                n = end - start
                if n < 6 or n > len(nb) - start + 3:
                    continue
                piece = b[start:end]
                for src, fl, name, pat, sz, wild in by_len.get(n, []):
                    if equal(pat, wild, sz, piece):
                        seg, off = va.split(":")
                        v = "%s:%04x" % (seg, int(off, 16) + start)
                        if v in known or (v, name) in claimed:
                            continue
                        claimed.add((v, name))
                        hits.append((v, n, name, src, fl))
    print(f"# {len(hits)} candidate hits (each still needs match.py + verify.py)")
    for v, n, name, src, fl in hits[:200]:
        print(f"{v}\t{n}\t{name}\t{src}\t{fl}")


if __name__ == "__main__":
    main()
