"""Sweep the `register` keyword over a parameter list and report which variant matches.

The most common near-miss in this project is "the original keeps this value in a register
and MSC keeps it in the frame" (or the other way round).  Which parameters MSC decides to
register-ise is not predictable from the source, so the cheap way to find out is to try
every subset at once: all variants go into **one** translation unit (they differ only in
their declarations), one compile produces them all, and `match.py`'s comparison decides.

The template contains a function named `CAND`; every parameter in its list is a candidate
for `register`.  Two to four parameters gives 4 to 16 variants, which is one compile.

    python tools/regsweep.py 2a7e:0000 67 build/sweep.c --flags "/G1 /AM /Gs /Ox"

`--flags` may be repeated; each flag set is compiled in turn, so `--flags "/G1 /AM /Gs /Os"`
plus `--flags "/G1 /AM /Gs /Ox"` covers both optimisers in two compiles.
"""
import argparse
import itertools
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

HEAD = re = None  # noqa: F841  (imported lazily below to keep the file readable)


def split_params(text):
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def variants(src):
    """Yield (name, source) for every register subset of CAND's parameter list."""
    import re as _re
    m = _re.search(r"([A-Za-z_][\w \t]*?)\bCAND\s*\(([^)]*)\)", src)
    if not m:
        raise SystemExit("template has no `CAND(...)` function")
    ret, plist = m.group(1).strip(), split_params(m.group(2))
    for mask in itertools.product((0, 1, 2, 3), repeat=len(plist)):
        params = []
        for use, p in zip(mask, plist):
            if use & 2:
                p = _re.sub(r"^(?:unsigned |signed )?(int|short|char|long)\b",
                            lambda mm: "unsigned " + mm.group(1), p)
            if use & 1:
                p = "register " + p
            params.append(p)
        tag = "".join(str(b) for b in mask)
        name = "CAND" + tag
        body = src[:m.start()] + ret + " " + name + "(" + ", ".join(params) + ")" + src[m.end():]
        body = body.replace("CAND", name)
        yield name, body, mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("va")
    ap.add_argument("size", type=int)
    ap.add_argument("template")
    ap.add_argument("--flags", action="append", default=[])
    ap.add_argument("--msc-dir", default="MSC7I")
    ap.add_argument("--show", action="store_true", help="print the matching source")
    a = ap.parse_args()
    flags = a.flags or ["/G1 /AM /Gs /Os"]

    src = open(a.template, encoding="utf-8").read()
    names = []
    chunks = []
    for name, body, mask in variants(src):
        names.append((name, mask))
        # keep only the variant's own function: strip the original CAND definition
        chunks.append(body)
    # each variant still contains the other functions from the template; compile them all
    # in one file by concatenating with guards would duplicate - instead compile one file
    # per variant only if the template has more than the CAND function.
    hits = []
    for flag in flags:
        for (name, mask), body in zip(names, chunks):
            path = os.path.join("build", "sweep_%s.c" % name)
            open(path, "w", encoding="ascii", newline="\n").write(body)
            r = subprocess.run([PY, "build.py", path, "--msc-dir", a.msc_dir,
                                "--flags", flag, "--force"],
                               cwd=ROOT, capture_output=True, text=True)
            obj = os.path.join("build", "sweep_%s.OBJ" % name)
            if not os.path.exists(obj):
                continue
            q = subprocess.run([PY, "tools/match.py", a.va, name, "--obj", obj,
                                "--size", str(a.size)],
                               cwd=ROOT, capture_output=True, text=True)
            line = (q.stdout or q.stderr).strip().splitlines()
            first = line[0] if line else "?"
            if "MATCH" in first or "RELOCS" in first:
                hits.append((flag, name, mask, first, body))
                print("HIT", flag, first)
            elif a.show:
                print("   ", flag, name, first)
    if not hits:
        print("# no variant matched (%d variants x %d flag sets)" % (len(names), len(flags)))
    else:
        for flag, name, mask, first, body in hits:
            print("\n=== %s  %s  register-mask=%s" % (flag, first, mask))
            if a.show:
                print(body)


if __name__ == "__main__":
    main()
