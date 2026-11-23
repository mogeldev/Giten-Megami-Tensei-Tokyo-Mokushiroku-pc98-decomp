#!/usr/bin/env python3
"""build.py <source.c> [--flags "..."] — compiles ONE source file with MSC 7.0 (CL 8.00).

Wraps the complete DOS environment (template phase 2, details: docs/CONVENTIONS.md):
  * dosbox-x (not DOSBox 0.74 — MSC7's DOSX32 DPMI only runs with an external DPMI host)
  * HDPMI32 (HX-DOS runtime) as DPMI server TSR before every CL call
  * -nopromptfolder, APPDATA redirect into the workspace, SDL dummy driver, cycles=max
  * sources/objects: dds98\\src (drive D:) -> dds98\\build

Usage: python build.py src/calib/triv1.c --flags "/G1 /AH"
Prerequisite: toolchain\\msc7i (BIN/LIB/INCLUDE) and toolchain\\HDPMI32.EXE."""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))                     # dds98/
WS = os.path.abspath(os.path.join(ROOT, ".."))                        # weird_test
TC = os.path.join(WS, "toolchain")
DBX = os.path.join(TC, "dosboxx", "bin", "x64", "Release", "dosbox-x.exe")
STATE = os.path.join(WS, "dosboxx_home")
CONF = os.path.join(TC, "dosbox_run", "build.conf")
BUILD_DIR = os.path.join(ROOT, "build")
TIMEOUT_S = 120


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--flags", default="")
    ap.add_argument("--msc-dir", default="MSC7I",
                    help="DOS directory of the toolchain on drive C: "
                         "(MSC7I = MS C 7.0, MSC6I = MS C 6.00ax)")
    ap.add_argument("--no-dpmi", action="store_true",
                    help="do not load the HDPMI32 TSR (MSC 6.0 needs no DPMI)")
    ap.add_argument("--force", action="store_true",
                    help="rebuild even if the cache stamp matches")
    a = ap.parse_args()

    src_abs = os.path.abspath(os.path.join(ROOT, a.source))
    if not os.path.isfile(src_abs):
        sys.exit(f"ERROR: source missing: {src_abs}")
    stem = os.path.splitext(os.path.basename(a.source))[0]
    if len(stem) > 8:
        sys.exit(f"ERROR: '{stem}' is longer than 8 characters — MSC-CL (1992) "
                 "does not open long file names; please name the source 8.3-compliant")
    for need in (DBX, os.path.join(TC, "HDPMI32.EXE"),
                 os.path.join(TC, a.msc_dir.lower(), "BIN", "CL.EXE")):
        if not os.path.isfile(need):
            sys.exit(f"ERROR: toolchain missing: {need}")
    os.makedirs(BUILD_DIR, exist_ok=True)

    base = os.path.splitext(os.path.basename(a.source))[0]
    obj = f"D:\\BUILD\\{base}.OBJ"
    obj_path = os.path.join(BUILD_DIR, f"{base}.OBJ")
    stamp_path = os.path.join(BUILD_DIR, f"{base}.stamp")
    log_path = os.path.join(BUILD_DIR, f"{base}.CL.TXT")
    stamp = (f"flags={a.flags}\nmsc={a.msc_dir}\ndpmi={not a.no_dpmi}\n"
             f"src={os.path.getmtime(src_abs):.6f}\nsize={os.path.getsize(src_abs)}\n")
    if not a.force and os.path.isfile(obj_path) and os.path.isfile(stamp_path):
        with open(stamp_path, encoding="ascii") as f:
            if f.read() == stamp:
                print(f"CACHED: {obj_path} (flags/source unchanged)")
                return 0
    # Remove the previous outputs first: otherwise a failed compile leaves the old
    # OBJ in place and the "does the OBJ exist?" check below reports success with
    # a stale object (found in round 45 via a source edit that silently did not
    # take effect).
    for p in (obj_path, stamp_path, log_path):
        if os.path.isfile(p):
            os.remove(p)
    src_d = "D:\\" + os.path.dirname(a.source).replace("/", "\\").upper()
    src_f = f"{src_d}\\{os.path.basename(a.source).upper()}"

    lines = [
        f'mount C "{TC}"',
        f'mount D "{ROOT}"',
        "C:",
        f"SET PATH=C:\\{a.msc_dir}\\BIN",
        f"SET INCLUDE=C:\\{a.msc_dir}\\INCLUDE",
        f"SET LIB=C:\\{a.msc_dir}\\LIB",
    ]
    if not a.no_dpmi:
        lines.append("HDPMI32")
    lines.append(f'{a.msc_dir}\\BIN\\CL.EXE /c {a.flags} /Fo{obj} {src_f} '
                 f'> D:\\BUILD\\{base}.CL.TXT')
    conf = "[cpu]\r\ncycles=max\r\n[autoexec]\r\n" + "\r\n".join(lines) + "\r\nexit\r\n"
    with open(CONF, "w", encoding="ascii", newline="") as f:
        f.write(conf)

    env = os.environ.copy()
    roam = os.path.join(STATE, "AppData", "Roaming")
    loc = os.path.join(STATE, "AppData", "Local")
    for d in (roam, loc):
        os.makedirs(d, exist_ok=True)
    env["APPDATA"], env["LOCALAPPDATA"], env["USERPROFILE"] = roam, loc, STATE
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    try:
        subprocess.run([DBX, "-nopromptfolder", "-conf", CONF], cwd=os.path.join(TC, "dosbox_run"),
                       env=env, timeout=TIMEOUT_S, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        sys.exit(f"ERROR: run exceeded {TIMEOUT_S}s — dosbox-x killed")

    obj_path = os.path.join(BUILD_DIR, f"{base}.OBJ")
    if os.path.isfile(obj_path):
        with open(stamp_path, "w", encoding="ascii") as f:
            f.write(stamp)
        print(f"OK: {obj_path} ({os.path.getsize(obj_path)} Bytes)")
        return 0
    log = os.path.join(BUILD_DIR, f"{base}.CL.TXT")
    if os.path.isfile(log):
        with open(log, encoding="latin-1", errors="replace") as f:
            print(f.read()[-2000:])
    sys.exit("ERROR: no OBJ produced")


if __name__ == "__main__":
    main()
