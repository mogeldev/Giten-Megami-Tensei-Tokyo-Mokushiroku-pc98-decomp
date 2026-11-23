#!/usr/bin/env python3
"""sweep.py — family sweeper (template phase 5, step 3: transcribe siblings).

For a named byte family it finds every occurrence at a real function boundary
that is not yet in the ledger (compared by LINEAR address), generates the C
source, compiles it once with the calibrated flags and matches every member.

The size always comes from the matched byte run itself (the family regex ends at
the return instruction), never from the inventory, which is unreliable for these
small units.

Usage:
  python tools/sweep.py --list
  python tools/sweep.py byte_store            # report
  python tools/sweep.py byte_store --emit     # print ready ledger rows
"""
import argparse
import csv
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
FLAGS = "/G1 /AM /Gs /Os"

# name -> (regex, builder(hit) -> (decls, func, symbol))
# hit dict: d1,d2,imm,far,size,va,lin
FAMILIES = {
    "byte_store": (
        rb"\xC6\x06(?P<d1>..)(?P<imm>.)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["char %s;" % g(h["d1"])],
                   "%s %s(void) { %s = %d; }" % (conv(h), name(h), g(h["d1"]), h["imm"]),
                   name(h))),
    "word_inc": (
        rb"\xFF\x06(?P<d1>..)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { %s++; }" % (conv(h), name(h), g(h["d1"])), name(h))),
    "word_dec": (
        rb"\xFF\x0E(?P<d1>..)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { %s--; }" % (conv(h), name(h), g(h["d1"])), name(h))),
    "byte_inc": (
        rb"\xFE\x06(?P<d1>..)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["char %s;" % g(h["d1"])],
                   "%s %s(void) { %s++; }" % (conv(h), name(h), g(h["d1"])), name(h))),
    "word_copy": (
        rb"\xA1(?P<d1>..)\xA3(?P<d2>..)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["int %s;" % g(h["d1"]), "int %s;" % g(h["d2"])],
                   "%s %s(void) { %s = %s; }" % (conv(h), name(h), g(h["d2"]), g(h["d1"])),
                   name(h))),
    "byte_copy": (
        rb"\xA0(?P<d1>..)\xA2(?P<d2>..)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["char %s;" % g(h["d1"]), "char %s;" % g(h["d2"])],
                   "%s %s(void) { %s = %s; }" % (conv(h), name(h), g(h["d2"]), g(h["d1"])),
                   name(h))),
    "word_add_imm": (
        rb"\x83\x06(?P<d1>..)(?P<imm>.)(?P<ret>\xCB|\xC3)(?P<pad>\x90?)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { %s += %d; }" % (conv(h), name(h), g(h["d1"]), h["imm"]),
                   name(h))),
    # --- round 44: the cheap frameless shapes -------------------------------
    "word_get": (
        rb"\xA1(?P<d1>..)(?P<ret>\xCB|\xC3)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { return %s; }" % (conv(h), name(h), g(h["d1"])), name(h))),
    "byte_get": (
        rb"\xA1(?P<d1>..)\x2A\xE4(?P<ret>\xCB|\xC3)",
        lambda h: (["unsigned char %s;" % g(h["d1"])],
                   "%s %s(void) { return %s; }" % (conv(h), name(h), g(h["d1"])), name(h))),
    "word_set": (
        rb"\xA3(?P<d1>..)(?P<ret>\xCB|\xC3)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s __fastcall %s(int v) { %s = v; }" % (conv(h), name(h), g(h["d1"])),
                   "@" + name(h))),
    "inc_get": (
        rb"\xFF\x06(?P<d1>..)\xA1(?P<d2>..)(?P<ret>\xCB|\xC3)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { %s%s; return %s; }" % (conv(h), name(h), g(h["d1"]), "++", g(h["d1"])),
                   name(h))),
    "dec_get": (
        rb"\xFF\x0E(?P<d1>..)\xA1(?P<d2>..)(?P<ret>\xCB|\xC3)",
        lambda h: (["int %s;" % g(h["d1"])],
                   "%s %s(void) { %s--; return %s; }" % (conv(h), name(h), g(h["d1"]), g(h["d1"])),
                   name(h))),
}


def g(disp):
    return "g_%04x" % int.from_bytes(disp, "little")


def name(h):
    return "f_%04x_%04x" % (h["lin"] >> 4, h["lin"] & 0xF)


def conv(h):
    return "__far" if h["far"] else "__near"


def starts_and_ledger():
    # Prefer the split inventory: the decompiler merged functions, so relying on
    # functions.csv hides every unit inside a merged entry (see tools/split.py).
    units = os.path.join(ROOT, "ground_truth", "units.csv")
    if os.path.isfile(units):
        starts = {int(r["linear"], 16) - 0x10000: (r["va"], int(r["size"]))
                  for r in csv.DictReader(open(units))}
    else:
        inv = {r["va"]: (int(r["linear"], 16), int(r["size"]))
               for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "functions.csv")))
               if r.get("section") != "DATA"}
        starts = {lin - 0x10000: (va, size) for va, (lin, size) in inv.items()}
    ledger = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    done = {int(m.group(1), 16) * 16 + int(m.group(2), 16)
            for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", ledger, re.M)}
    return starts, done


def find(family):
    pat = re.compile(FAMILIES[family][0], re.S)
    starts, done = starts_and_ledger()
    hits = []
    for m in pat.finditer(IMG):
        off = m.start()
        if off not in starts:
            continue
        va, _inv_size = starts[off]
        lin = off + 0x10000
        if lin in done:
            continue
        d = {k: m.group(k) for k in ("d1", "d2", "imm") if m.groupdict().get(k)}
        h = {
            "va": va,
            "lin": lin,
            "size": m.end("ret") - m.start(),
            "far": m.group("ret") == b"\xCB",
            "bytes": IMG[off:off + (m.end("ret") - m.start())].hex(),
        }
        if "imm" in d:
            h["imm"] = int.from_bytes(d["imm"], "little")
        if "d1" in d:
            h["d1"] = d["d1"]
        if "d2" in d:
            h["d2"] = d["d2"]
        hits.append(h)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("family", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--emit", action="store_true", help="print ledger rows for matches")
    a = ap.parse_args()
    if a.list or not a.family:
        print("families:", ", ".join(sorted(FAMILIES)))
        return
    if a.family not in FAMILIES:
        sys.exit(f"unknown family {a.family!r}; use --list")

    hits = find(a.family)
    print(f"{a.family}: {len(hits)} hits at function boundaries not in ledger")
    if not hits:
        return

    decls, funcs, meta = [], [], []
    for h in hits:
        d, f, sym = FAMILIES[a.family][1](h)
        decls += [x for x in d if x not in decls]
        funcs.append(f)
        meta.append((h, sym))
        print(f"  {h['va']}  {h['size']:>2}B  {h['bytes']}  {f}")

    src = "/* generated by tools/sweep.py - family %s */\n%s\n\n%s\n" % (
        a.family, "\n".join(decls), "\n\n".join(funcs))
    stem = "sw" + a.family.replace("_", "")[:6]  # 8.3-safe: max 8 chars
    src_rel = os.path.join("src", "calib", stem + ".c")
    with open(os.path.join(ROOT, src_rel), "w", encoding="ascii") as fh:
        fh.write(src)
    print(f"\nwrote {src_rel} ({stem}.c)")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py"), src_rel.replace(os.sep, "/"),
                        "--flags", FLAGS], capture_output=True, text=True)
    print((r.stdout or "").strip().splitlines()[-1] if r.stdout else "")
    if r.returncode != 0:
        print((r.stdout or "")[-1500:], (r.stderr or "")[-1500:])
        sys.exit(1)

    obj = os.path.join(ROOT, "build", stem + ".OBJ")
    ok = 0
    rows = []
    for h, sym in meta:
        q = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "match.py"),
                            h["va"], sym, "--obj", obj, "--size", str(h["size"])],
                           capture_output=True, text=True)
        status = "RELOCS" if q.returncode == 0 else "DIFF"
        ok += q.returncode == 0
        print(f"  {h['va']} {sym}: {status}")
        if q.returncode != 0:
            print("    " + ((q.stdout or "") + (q.stderr or "")).strip()[:300])
        else:
            rows.append(f"| {h['va']} | {sym} | {h['size']} | RELOCS | "
                        f"src={src_rel.replace(os.sep, '/')}; flags=\"{FLAGS}\"; {a.family} |")
    print(f"\n{ok}/{len(meta)} verified with flags {FLAGS} in {src_rel}")
    if a.emit and rows:
        print("\nledger rows:")
        print("\n".join(rows))


if __name__ == "__main__":
    main()
