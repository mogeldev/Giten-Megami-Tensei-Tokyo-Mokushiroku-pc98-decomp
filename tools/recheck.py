"""Re-test the PENDING ledger rows in one pass.

Every PENDING row is a unit whose C is believed correct and which misses by a byte or two.
Keeping those sources in `src/calib/pending*.c` and their addresses here means a new flag, a
new compiler or a new idea can be tested against **all** of them at once instead of one
round per unit.

`tools/pending.txt` holds one row per line:

    <src> | <flags> | <MSC dir> | <va> <symbol> <size>

Run it after changing anything that could matter - or when a wall is finally explained:

    python tools/recheck.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
MANIFEST = os.path.join(HERE, "pending.txt")


def rows():
    out = []
    for line in open(MANIFEST, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        src, flags, msc, rest = [p.strip() for p in line.split("|", 3)]
        va, sym, size = rest.split()
        out.append((src, flags, msc, va, sym, int(size)))
    return out


def main():
    entries = rows()
    objs = {}
    hits = 0
    for src, flags, msc, va, sym, size in entries:
        key = (src, flags, msc)
        if key not in objs:
            cmd = [PY, os.path.join(ROOT, "build.py"), src, "--flags", flags, "--force"]
            if msc and msc != "-":
                cmd += ["--msc-dir", msc]
            q = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            obj = os.path.join(ROOT, "build",
                               os.path.splitext(os.path.basename(src))[0].replace("calib/", "") + ".OBJ")
            objs[key] = obj if os.path.exists(obj) else None
        obj = objs[key]
        if not obj:
            print(f"  {va}: source did not compile ({src})")
            continue
        q = subprocess.run([PY, os.path.join(ROOT, "tools", "match.py"), va, sym,
                            "--obj", obj, "--size", str(size)],
                           cwd=ROOT, capture_output=True, text=True)
        first = ((q.stdout or q.stderr).strip().splitlines() or ["?"])[0]
        flag = "**" if ("MATCH" in first or "RELOCS" in first) else "  "
        if flag == "**":
            hits += 1
        print(f"{flag} {first}")
    print(f"\n# {hits} of {len(entries)} pending rows now match")


if __name__ == "__main__":
    main()
