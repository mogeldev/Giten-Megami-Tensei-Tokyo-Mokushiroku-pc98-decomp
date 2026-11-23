#!/usr/bin/env python3
"""verify.py — rechecks ALL MATCHING.md rows; aborts on regression
(template phase 6).

Integrity: for every (src, flags) combination the source is **recompiled** with
`build.py` and then every associated ledger row is checked against the original
bytes. The result therefore does not depend on which OBJ currently sits in
`build/` (lesson from round 23). `--fast` skips the rebuild (for quick
intermediate checks only, not for close-out).

Size comes from the ledger column (real length), not from the inventory.
Counters are recomputed from the ledger, never from memory."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
BUILD = os.path.join(ROOT, "build")
NOTE_RE = re.compile(r'src=(\S+);\s*flags="([^"]*)"')
# Optional toolchain selectors in the note (default: MSC 7.0 under DOSBox-X+HDPMI):
#   msc=MSC6C   compile with that toolchain directory (build.py --msc-dir)
#   nodpmi      do not load the HDPMI TSR (MSC 6.0's real-mode CL hangs with it)
MSC_RE = re.compile(r"\bmsc=(\w+)")
DPMI_RE = re.compile(r"\bnodpmi\b")
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]


def build_cmd(src, flags, msc, nodpmi):
    cmd = [PY, os.path.join(ROOT, "build.py"), src, "--flags", flags]
    if msc:
        cmd += ["--msc-dir", msc]
    if nodpmi:
        cmd.append("--no-dpmi")
    return cmd


def parse_ledger():
    rows, bad = [], []
    with open(os.path.join(ROOT, "docs", "MATCHING.md"), encoding="utf-8") as f:
        for line in f:
            if not re.match(r"^\|\s*[0-9a-f]{4}:[0-9a-f]{4}\s*\|", line):
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 5:
                bad.append(f"incomplete row: {line.strip()[:80]}")
                continue
            rows.append({"va": parts[0], "name": parts[1], "size": parts[2],
                         "status": parts[3], "note": parts[4]})
    return rows, bad


def window_problem(b):
    """Return a complaint if the window is not exactly one function.

    Two failure modes that a plain byte comparison cannot see:
      - too SHORT: narrowing the comparison always passes (three rows recorded
        12/24/20 bytes for functions of 13/25/19);
      - too LONG: a trailing NOP/padding byte that the object also happens to
        emit makes the row pass while the recorded length is not the function.
    """
    core = b
    while core and core[-1] == 0x90:
        core = core[:-1]
    if not core:
        return "window is empty or only padding"
    ok = core[-1] in (0xC3, 0xCB, 0xCF) or (len(core) >= 3 and core[-3] in (0xCA, 0xC2))
    if not ok:
        return (f"does not end at a return instruction (ends {core[-4:].hex()}) "
                f"- size too short")
    if len(core) != len(b):
        return (f"includes {len(b) - len(core)} trailing padding byte(s) "
                f"- real length is {len(core)}")
    return None


def status_matches(row, output):
    # ASM describes the source, not the matcher's relocation result.
    return row["status"] == "ASM" or output.startswith(
        f"{row['va']} {row['name']}: {row['status']}  (")


def main():
    if "--selftest" in sys.argv:
        row = {"va": "1000:0000", "name": "TEST", "status": "MATCH"}
        exact = "1000:0000 TEST: MATCH  (size=4, reloc-masked=0)"
        masked = "1000:0000 TEST: RELOCS  (size=4, reloc-masked=2)"
        assert status_matches(row, exact) and not status_matches(row, masked)
        row["status"] = "RELOCS"
        assert status_matches(row, masked) and not status_matches(row, exact)
        row["status"] = "ASM"
        assert status_matches(row, masked)
        print("verify selftest: ok")
        return
    fast = "--fast" in sys.argv
    rows, fails = parse_ledger()

    # Duplicates (linear address) and size 0 are forbidden (template phase 6)
    seen = set()
    for r in rows:
        seg, off = r["va"].split(":")
        lin = int(seg, 16) * 16 + int(off, 16)
        if lin in seen:
            fails.append(f"DUP {r['va']}")
        seen.add(lin)
        if int(r["size"]) == 0:
            fails.append(f"SIZE-0 {r['va']} (comparing 0 bytes always matches)")

    # Group by (src, flags[, msc name, nodpmi]); build once per combination
    groups = {}
    for r in rows:
        if r["status"] == "PENDING":
            continue
        m = NOTE_RE.search(r["note"])
        if not m:
            fails.append(f"{r['va']}: MATCH/RELOCS without src=/flags= in the note")
            continue
        msc = (MSC_RE.search(r["note"]) or [None, ""])[1].upper()
        nodpmi = bool(DPMI_RE.search(r["note"]))
        groups.setdefault(m.groups() + (msc, nodpmi), []).append(r)

    # One OBJ per source stem: two toolchains on the same stem would overwrite
    # each other's object between build and match, so refuse it.
    stems = {}
    for (src, _f, msc, _n) in groups:
        stem = os.path.splitext(os.path.basename(src))[0]
        stems.setdefault(stem, set()).add((src, msc))
    for stem, users in stems.items():
        if len(users) > 1:
            fails.append(f"source stem '{stem}' is compiled with several toolchains: "
                         f"{sorted(users)} — give each its own 8.3 filename")

    objs = {}
    for (src, flags, msc, nodpmi), items in groups.items():
        stem = os.path.splitext(os.path.basename(src))[0]
        obj = os.path.join(BUILD, f"{stem}.OBJ")
        if not fast:
            r = subprocess.run(build_cmd(src, flags, msc, nodpmi),
                               capture_output=True, text=True)
            tag = "CACHED" if (r.stdout or "").startswith("CACHED") else "built"
            extra = f" msc={msc}" if msc else ""
            print(f"{tag:<6} {src} [{flags}]{extra}", flush=True)
            if r.returncode != 0:
                fails.append(f"BUILD FAILED {src} [{flags}]{extra}\n"
                             f"{(r.stdout or '')[-400:]}{(r.stderr or '')[-400:]}")
                continue
        objs[(src, flags, msc, nodpmi)] = obj

    n_match = n_relocs = n_asm = n_pending = 0
    for r in rows:
        if r["status"] == "PENDING":
            n_pending += 1
            continue
        m = NOTE_RE.search(r["note"])
        key = (m.groups() + ((MSC_RE.search(r["note"]) or [None, ""])[1].upper(),
                             bool(DPMI_RE.search(r["note"])))) if m else None
        obj = objs.get(key) if key else None
        if not obj:
            continue
        seg, off = r["va"].split(":")
        lin = int(seg, 16) * 16 + int(off, 16)
        size = int(r["size"])
        window = IMG[lin - 0x10000: lin - 0x10000 + size]
        problem = window_problem(window)
        if problem:
            fails.append(f"{r['va']}: {problem}")
        cmd = [PY, os.path.join(ROOT, "tools", "match.py"), r["va"], r["name"],
               "--obj", obj, "--size", r["size"]]
        q = subprocess.run(cmd, capture_output=True, text=True)
        out = ((q.stdout or "") + (q.stderr or "")).strip()
        if q.returncode != 0:
            fails.append(f"{r['va']} {r['name']}: REGRESSION\n{out[:500]}")
            print(f"  {r['va']} {r['name']}: ERROR")
        elif not status_matches(r, out):
            fails.append(f"{r['va']} {r['name']}: expected {r['status']}\n{out[:500]}")
        else:
            if r["status"] == "MATCH":
                n_match += 1
            elif r["status"] == "ASM":
                n_asm += 1
            else:
                n_relocs += 1
            print(f"  {r['va']} {r['name']}: {r['status']} ok")

    print(f"Ledger: {len(rows)} rows — MATCH {n_match}, RELOCS {n_relocs}, ASM {n_asm}, "
          f"PENDING {n_pending}")
    if fails:
        print("ERRORS:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("verify: green")


if __name__ == "__main__":
    main()
