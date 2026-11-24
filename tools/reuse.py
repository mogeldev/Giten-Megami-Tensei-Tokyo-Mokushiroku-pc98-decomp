#!/usr/bin/env python3
"""reuse.py - find unmatched units that are byte-identical (modulo call targets)
to an already verified row, and re-verify them against the same symbol.

Fast path: every ledger row is reduced to a normalised pattern (all direct call
targets masked: `90 0E E8 rel16`, `9A seg off`, `E8 rel16`). Every unmatched
unit is normalised the same way; an exact pattern match plus equal length makes
it a sibling of that row, and `match.py` confirms it before anything is printed
or written. This is how the six `36e7` siblings were found by hand.
"""
import argparse
import csv
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
ROW = re.compile(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
                 r"\s*(\w+)\s*\|\s*(.*?)\s*\|$")


def linear(va):
    s, o = va.split(":")
    return int(s, 16) * 16 + int(o, 16)


def norm_shape(b):
    """Like norm(), but also masks absolute data addresses.

    Two functions that differ only in *which* globals they touch have the same shape, and
    the C differs only in the identifier - so masking `A1`/`A3`/`C7`/`68`/`[bx+disp16]`
    operands turns them into candidates. `match.py` still has to confirm each one.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("dds98_dis", os.path.join(ROOT, "tools", "dis.py"))
    dismod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dismod)
    out = bytearray(norm(b))
    i = 0
    while i < len(b):
        try:
            _, ln = dismod.decode(b, i)
        except Exception:
            ln = 1
        op = b[i]
        if op in (0xA1, 0xA3, 0xA0, 0xA2) and ln == 3:
            out[i + 1:i + 3] = b"\x00" * 2
        elif op == 0xC7 and ln >= 5:
            out[i + 2:i + 4] = b"\x00" * 2       # modrm + disp16 for [disp16]
        i += max(ln, 1)
    return bytes(out)


def norm(b):
    """Mask call targets and far-pointer immediates, walking instruction by instruction.

    A byte scan is not enough: a `68 imm16` whose immediate happens to contain an 0xE8 byte
    is indistinguishable from a call, and the old scan masked the wrong two bytes and left
    the real `9A` target in place (which is why the `2daa` / `2dad` pair was missed for a
    round). Decoding first is the only reliable way to know where operands start.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("dds98_dis", os.path.join(ROOT, "tools", "dis.py"))
    dismod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dismod)
    out = bytearray(b)
    i = 0
    while i < len(b):
        try:
            _, ln = dismod.decode(b, i)
        except Exception:
            ln = 1
        if b[i] == 0x9A and ln == 5:
            out[i + 1:i + 5] = b"\x00" * 4
        elif b[i] == 0xE8 and ln == 3:
            out[i + 1:i + 3] = b"\x00" * 2
        elif b[i] == 0x68 and ln == 3:
            out[i + 1:i + 3] = b"\x00" * 2
        elif b[i:i + 2] == b"\x1e\x68" and ln == 4:
            out[i + 2:i + 4] = b"\x00" * 2
            i += 4
            continue
        i += max(ln, 1)
    return bytes(out)


def ledger():
    out = []
    for line in open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8"):
        m = ROW.match(line.strip())
        if not m or m.group(5) not in ("MATCH", "RELOCS"):
            continue
        note = m.group(6)
        src = re.search(r"src=(\S+);", note)
        flags = re.search(r'flags="([^"]*)"', note)
        if not src or not flags:
            continue
        msc = re.search(r"\bmsc=(\w+)", note)
        out.append({"va": f"{m.group(1)}:{m.group(2)}", "name": m.group(3).strip(),
                    "size": int(m.group(4)), "src": src.group(1), "flags": flags.group(1),
                    "msc": msc.group(1) if msc else "", "nodpmi": "nodpmi" in note})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--shape", action="store_true",
                    help="also mask absolute data addresses (same shape, different globals)")
    a = ap.parse_args()
    known = ledger()
    seen = {r["va"] for r in known}
    seen_lin = {linear(r["va"]) for r in known}
    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))

    # pattern -> (row, normalised bytes) of every verified row
    pats = {}
    for r in known:
        b = IMG[linear(r["va"]) - 0x10000: linear(r["va"]) - 0x10000 + r["size"]]
        nf = norm_shape if a.shape else norm
        pats.setdefault((nf(b), r["size"]), []).append(r)

    cands = []
    for lin, (va, size) in units.items():
        if va in seen or lin in seen_lin:
            continue
        b = IMG[lin - 0x10000: lin - 0x10000 + size]
        core = b.rstrip(b"\x90")
        if not core:
            continue
        nf = norm_shape if a.shape else norm
        for (pat, psize), rs in pats.items():
            if psize <= len(core) and nf(core[:psize]) == pat:
                cands.append((va, rs[0], psize))
                break
    print(f"# {len(cands)} candidate siblings")

    # rebuild the objects we need
    objs = {}
    hits = []
    for va, r, size in cands[:a.limit]:
        key = (r["src"], r["flags"], r["msc"], r["nodpmi"])
        if key not in objs:
            cmd = [PY, os.path.join(ROOT, "build.py"), r["src"], "--flags", r["flags"], "--force"]
            if r["msc"]:
                cmd += ["--msc-dir", r["msc"]]
            if r["nodpmi"]:
                cmd += ["--no-dpmi"]
            q = subprocess.run(cmd, capture_output=True, text=True)
            obj = os.path.join(ROOT, "build", os.path.splitext(os.path.basename(r["src"]))[0] + ".OBJ")
            objs[key] = obj if q.returncode == 0 else None
        obj = objs[key]
        if not obj:
            continue
        q = subprocess.run([PY, os.path.join(ROOT, "tools", "match.py"), va, r["name"],
                            "--obj", obj, "--size", str(size)], capture_output=True, text=True)
        out = (q.stdout or "").strip().splitlines()
        if out and ("RELOCS" in out[0] or "MATCH" in out[0]):
            hits.append((va, r, size))
            print(f"  {va} = {r['name']} ({r['src']}, {size} B)")
        else:
            print(f"  {va}: pattern-sibling but diff ({out[0] if out else '?'})")

    print(f"\n# {len(hits)} verified siblings")
    for va, r, size in hits:
        note = f'src={r["src"]}; flags="{r["flags"]}";'
        if r["msc"]:
            note += f' msc={r["msc"]};'
        if r["nodpmi"]:
            note += " nodpmi;"
        note += " byte-identical to a verified sibling modulo call targets"
        print(f'| {va} | {r["name"]} | {size} | RELOCS | {note} |')
    if a.write and hits:
        p = os.path.join(ROOT, "docs", "MATCHING.md")
        text = open(p, encoding="utf-8").read().rstrip("\n")
        add = []
        for va, r, size in hits:
            note = f'src={r["src"]}; flags="{r["flags"]}";'
            if r["msc"]:
                note += f' msc={r["msc"]};'
            if r["nodpmi"]:
                note += " nodpmi;"
            note += " byte-identical to a verified sibling modulo call targets"
            add.append(f"| {va} | {r['name']} | {size} | RELOCS | {note} |")
        open(p, "w", encoding="utf-8", newline="\n").write(text + "\n" + "\n".join(add) + "\n")
        print(f"# appended {len(add)} rows")


if __name__ == "__main__":
    main()
