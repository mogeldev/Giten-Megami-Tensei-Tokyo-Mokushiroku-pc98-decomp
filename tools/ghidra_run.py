"""Shared Ghidra headless starter (all tools/ use it identically).

Wraps the sandbox workaround: Ghidra 12 writes log/OSGi cache to %APPDATA%.
In DSH sandbox operation only the workspace is writable -> APPDATA/LOCALAPPDATA/
USERPROFILE/TEMP are redirected into the workspace. Output goes to log files
(no pipes)."""
import os
import subprocess

WS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # weird_test
GHIDRA_BAT = os.path.join(WS, "ghidra_12.2_PUBLIC", "support", "analyzeHeadless.bat")
PROJ_DIR = os.path.join(WS, "ghidra_proj")
PROJ_NAME = "GitenDecomp"
SCRIPT_PATH = os.path.join(WS, "ghidra_scripts")


def run(program, post_args, log_path):
    """Runs -process (already analyzed program, no re-analysis)."""
    env = os.environ.copy()
    gh = os.path.join(WS, "ghidra_home")
    roam = os.path.join(gh, "AppData", "Roaming")
    loc = os.path.join(gh, "AppData", "Local")
    tmp = os.path.join(WS, "ghidra_tmp")
    for d in (roam, loc, tmp, PROJ_DIR):
        os.makedirs(d, exist_ok=True)
    env["APPDATA"], env["LOCALAPPDATA"], env["USERPROFILE"] = roam, loc, gh
    env["TEMP"] = env["TMP"] = tmp
    cmd = [GHIDRA_BAT, PROJ_DIR, PROJ_NAME, "-process", program, "-noanalysis",
           "-scriptPath", SCRIPT_PATH, *post_args]
    with open(log_path, "w") as fh:
        return subprocess.run(cmd, stdout=fh, stderr=fh, env=env).returncode
