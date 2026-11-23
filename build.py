#!/usr/bin/env python3
"""build.py <quelle.c> [--flags "..."] — kompiliert EINE Quelldatei mit MSC 7.0 (CL 8.00).

Kapselt die komplette DOS-Umgebung (Vorlage Phase 2, Details: docs/CONVENTIONS.md):
  * dosbox-x (nicht DOSBox 0.74 — MSC7s DOSX32-DPMI laeuft nur mit externem DPMI-Host)
  * HDPMI32 (HX-DOS-Runtime) als DPMI-Server-TSR vor jedem CL-Aufruf
  * -nopromptfolder, APPDATA-Redirect in den Workspace, SDL-Dummy-Treiber, cycles=max
  * Quellen/Objekte: dds98\\src (Drive D:) -> dds98\\build

Aufruf: python build.py src/calib/triv1.c --flags "/G1 /AH"
Voraussetzung: toolchain\\msc7i (BIN/LIB/INCLUDE) und toolchain\\HDPMI32.EXE."""
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
    a = ap.parse_args()

    src_abs = os.path.abspath(os.path.join(ROOT, a.source))
    if not os.path.isfile(src_abs):
        sys.exit(f"FEHLER: Quelle fehlt: {src_abs}")
    for need in (DBX, os.path.join(TC, "HDPMI32.EXE"),
                 os.path.join(TC, "msc7i", "BIN", "CL.EXE")):
        if not os.path.isfile(need):
            sys.exit(f"FEHLER: Toolchain fehlt: {need}")
    os.makedirs(BUILD_DIR, exist_ok=True)

    base = os.path.splitext(os.path.basename(a.source))[0]
    obj = f"D:\\BUILD\\{base}.OBJ"
    src_d = "D:\\" + os.path.dirname(a.source).replace("/", "\\").upper()
    src_f = f"{src_d}\\{os.path.basename(a.source).upper()}"

    lines = [
        f'mount C "{TC}"',
        f'mount D "{ROOT}"',
        "C:",
        "SET PATH=C:\\MSC7I\\BIN",
        "SET INCLUDE=C:\\MSC7I\\INCLUDE",
        "SET LIB=C:\\MSC7I\\LIB",
        "HDPMI32",
        f'MSC7I\\BIN\\CL.EXE /c {a.flags} /Fo{obj} {src_f} > D:\\BUILD\\{base}.CL.TXT',
    ]
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
        sys.exit(f"FEHLER: Lauf ueber {TIMEOUT_S}s — dosbox-x gekillt")

    obj_path = os.path.join(BUILD_DIR, f"{base}.OBJ")
    if os.path.isfile(obj_path):
        print(f"OK: {obj_path} ({os.path.getsize(obj_path)} Bytes)")
        return 0
    log = os.path.join(BUILD_DIR, f"{base}.CL.TXT")
    if os.path.isfile(log):
        with open(log, encoding="latin-1", errors="replace") as f:
            print(f.read()[-2000:])
    sys.exit("FEHLER: kein OBJ erzeugt")


if __name__ == "__main__":
    main()
