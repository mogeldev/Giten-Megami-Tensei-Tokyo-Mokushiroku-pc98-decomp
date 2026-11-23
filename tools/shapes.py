#!/usr/bin/env python3
"""shapes.py - generator for the two-call relay templates (round 10).

Grammar accepted (LINK-/F translated calls, see CONVENTIONS.md):

    55 8B EC [56] [57]  <push>*  CALL  <push>*  CALL  [5E] [5F]  C9 (CA imm|CB)

where a push is `FF 76 xx` (argument slot), `6A i8` / `68 i16` (constant),
`56`/`57` (register copy of an argument loaded via `8B 76/7E xx`) and `50`
(the previous call's result). Anything else cancels the unit: no guessing.

It emits `src/calib/<stem>.c`, builds it once, matches every unit and prints
ready ledger rows (`--write` appends them).
"""
import argparse
import csv
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
PY = sys.executable
CALL = b"\x90\x0e\xe8"


def ledger_done():
    text = open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read()
    return {int(m.group(1), 16) * 16 + int(m.group(2), 16)
            for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", text, re.M)}


def parse(b):
    """-> (nargs, (arg1s, arg2s)) or None. arg = ('p', idx) | ('c', value) | ('r', 1)."""
    if b[:3] != b"\x55\x8b\xec":
        return None
    i = 3
    reg = {}                                   # si/di/ax -> ('p', idx) | ('c', value)
    for r in (0x56, 0x57):                     # optional save pushes
        if i < len(b) and b[i] == r:
            i += 1
    calls, pushes = [], []
    while i < len(b):
        op = b[i]
        if b[i:i + 3] == CALL:
            if len(calls) == 2:
                return None
            calls.append(list(pushes))
            pushes = []
            i += 5
            continue
        if b[i:i + 2] == b"\xff\x76":
            pushes.append(("p", b[i + 2]))
            i += 3
            continue
        if op == 0x6A:
            pushes.append(("c", int.from_bytes(b[i + 1:i + 2], "little", signed=True)))
            i += 2
            continue
        if op == 0x68:
            pushes.append(("c", int.from_bytes(b[i + 1:i + 3], "little", signed=True)))
            i += 3
            continue
        if op in (0x50, 0x51, 0x52, 0x53, 0x56, 0x57):
            key = {0x50: "ax", 0x51: "cx", 0x52: "dx", 0x53: "bx",
                   0x56: "si", 0x57: "di"}[op]
            if key not in reg:
                return None
            pushes.append(reg[key])
            i += 1
            continue
        if b[i:i + 2] == b"\xff\x36":          # push word [disp16]
            pushes.append(("g", int.from_bytes(b[i + 2:i + 4], "little")))
            i += 4
            continue
        if b[i:i + 2] in (b"\x8b\x76", b"\x8b\x7e", b"\x8b\x46", b"\x8b\x5e",
                           b"\x8b\x4e", b"\x8b\x56"):
            key = {0x76: "si", 0x7E: "di", 0x46: "ax", 0x5E: "bx",
                   0x4E: "cx", 0x56: "dx"}[b[i + 1]]
            reg[key] = ("p", b[i + 2])
            i += 3
            continue
        if op == 0xA1:                          # mov ax,[disp16]
            reg["ax"] = ("g", int.from_bytes(b[i + 1:i + 3], "little"))
            i += 3
            continue
        if op == 0x5E or op == 0x5F:           # restore push si/di
            i += 1
            continue
        if op == 0xC9:                         # leave
            if b[i + 1] == 0xCA and i + 3 < len(b):
                nargs = int.from_bytes(b[i + 2:i + 4], "little") // 2
                if nargs * 2 != int.from_bytes(b[i + 2:i + 4], "little"):
                    return None
                if len(calls) != 2 or not calls[0] or not calls[1]:
                    return None
                return nargs, calls
            return None
        return None
    return None


def param_name(slot, nargs):
    """Pascal slot at bp+slot -> parameter name (first parameter at the top)."""
    off = slot - 6
    if off < 0 or off % 2 or off // 2 > nargs - 1:
        return None
    return f"p{nargs - 1 - off // 2}"


def render(va, nargs, calls):
    """C source for one unit, or None if the shape does not translate cleanly."""
    a1, a2 = calls[0], calls[1]
    if any(k == "r" for k, _ in a1):
        return None
    # the first call's result may only appear once, at the front of the second list
    if any(k == "r" for k, _ in a2[1:]):
        return None
    uses_result = any(k == "r" for k, _ in a2)

    def text(arg):
        kind, val = arg
        if kind == "p":
            return param_name(val, nargs)
        if kind == "g":
            return f"g_{val:04x}"
        return str(val)

    t1 = [text(x) for x in a1]
    t2 = [text(x) for x in a2 if x[0] != "r"]
    if any(t is None for t in t1 + t2):
        return None
    name = "F_" + va.replace(":", "_").upper()
    params = ", ".join(f"int p{i}" for i in range(nargs))
    s1 = f"Sub{len(a1)}({', '.join(t1)})" if a1 else "Sub0()"
    second = []
    for arg in a2:
        second.append(s1 if arg[0] == "r" else text(arg))
    call2 = f"Sub{len(a2)}({', '.join(second)})"
    body = f"return {call2};" if uses_result else f"{s1}; return {call2};"
    head = f"int __far __pascal {name}({params})" if params else f"int __far __pascal {name}(void)"
    return name, params, f"{head} {{ {body} }}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default="cshape1")
    ap.add_argument("--flags", default="/G1 /AM /Gs /Os")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--max", type=int, default=200)
    a = ap.parse_args()
    if len(a.stem) > 8:
        sys.exit("ERROR: stem must be 8.3")
    src_rel = f"src/calib/{a.stem}.c"
    if src_rel in open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8").read():
        sys.exit(f"ERROR: {src_rel} already referenced")

    crt = {int(r["linear"], 16) for r in csv.DictReader(
        open(os.path.join(ROOT, "ground_truth", "foreign_crt.csv")))}
    done = ledger_done()
    units = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "ground_truth", "units.csv"))):
        units.setdefault(int(r["linear"], 16), (r["va"], int(r["size"])))

    todo = []
    for lin, (va, size) in sorted(units.items()):
        if lin in done or lin in crt or not (8 <= size <= 120):
            continue
        got = parse(IMG[lin - 0x10000: lin - 0x10000 + size])
        if not got:
            continue
        nargs, calls = got
        r = render(va, nargs, calls)
        if not r:
            continue
        todo.append((va, r, calls))
        if len(todo) >= a.max:
            break
    print(f"# {len(todo)} units translate to the two-call template")

    # group by (arity of call1, arity of call2) to keep the extern list small
    lines = ["/* generated by tools/shapes.py: two-call relay templates */"]
    seen = set()
    globs = set()
    for va, (name, params, body), calls in todo:
        for args in calls:
            for kind, val in args:
                if kind == "g":
                    globs.add(val)
    for g in sorted(globs):
        lines.append(f"extern int g_{g:04x};")
    for va, (name, params, body), calls in todo:
        for n in {len(calls[0]), len(calls[1])}:
            if n not in seen:
                seen.add(n)
                lines.append(f"extern int __far __pascal Sub{n}({', '.join('int' for _ in range(n))});" if n
                             else "extern int __far __pascal Sub0(void);")
        lines.append(body)
    open(os.path.join(ROOT, src_rel), "w", encoding="ascii", newline="\n").write("\n".join(lines) + "\n")

    r = subprocess.run([PY, os.path.join(ROOT, "build.py"), src_rel, "--flags", a.flags, "--force"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("BUILD FAILED\n" + (r.stdout or "")[-400:] + (r.stderr or "")[-400:])
    obj = os.path.join(ROOT, "build", a.stem + ".OBJ")

    rows = []
    for va, (name, params, body), calls in todo:
        q = subprocess.run([PY, os.path.join(ROOT, "tools", "match.py"), va, name,
                            "--obj", obj, "--size", str(_size(va, units))],
                           capture_output=True, text=True)
        out = (q.stdout or q.stderr).strip().splitlines()
        line = out[0] if out else "?"
        if "RELOCS" in line or "MATCH" in line:
            size = int(re.search(r"size=(\d+)", line).group(1))
            status = "MATCH" if "MATCH" in line else "RELOCS"
            rows.append((va, name, size, status, body))
            print(f"  {va} {name}: {status} ({size} B)")
        else:
            print(f"  {va} {name}: skip")
    print(f"\n# {len(rows)} verified rows")
    for va, name, size, status, body in rows:
        print(f"| {va} | {name} | {size} | {status} | src={src_rel}; flags=\"{a.flags}\"; "
              f"two-call relay `{body}`; image `90 0E E8` = LINK /F translation |")
    if a.write and rows:
        p = os.path.join(ROOT, "docs", "MATCHING.md")
        text = open(p, encoding="utf-8").read().rstrip("\n")
        add = [f"| {va} | {name} | {size} | {status} | src={src_rel}; flags=\"{a.flags}\"; "
               f"two-call relay `{body}`; image `90 0E E8` = LINK /F translation |"
               for va, name, size, status, body in rows]
        open(p, "w", encoding="utf-8", newline="\n").write(text + "\n" + "\n".join(add) + "\n")
        print(f"# appended {len(add)} rows")


def _size(va, units):
    lin = int(va.split(":")[0], 16) * 16 + int(va.split(":")[1], 16)
    return units[lin][1]


if __name__ == "__main__":
    main()
