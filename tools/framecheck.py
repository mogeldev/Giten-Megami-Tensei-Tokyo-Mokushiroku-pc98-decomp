"""framecheck.py - find framed function prologues the inventory does not know about.

`ground_truth/units.csv` comes out of the Ghidra inventory plus the splitter, and it
is not perfect: a few real functions start a byte or two before the boundary the
splitter chose (`3d59:000c` was recorded as a fragment at `3d59:000e`), and a few
functions are merged into one unit because they share code.

This scans the load image for `55 8B EC` (push bp; mov bp,sp) and reports every hit
that is NOT a unit start, together with the evidence that decides what it is:

  ret-before   the four bytes before the prologue end in a return instruction
               (with at most a couple of padding bytes) -> almost certainly a real
               function start the inventory missed
  inside       no return before it -> the prologue is inside a larger merged unit,
               which is expected and harmless

Usage:  python tools/framecheck.py [--verbose]
Exit code is always 0; this is a report, not a gate.
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE")
LOAD_IMAGE_AT = 896 * 16          # offset of the load image in the MZ file
LOAD_IMAGE_END = 339735
PROLOGUE = b"\x55\x8B\xEC"
RETURNS = (0xC3, 0xCB)            # retn / retf
RET_IMM = (0xC2, 0xCA)            # retn imm16 / retf imm16 (3 bytes)


def main():
    verbose = "--verbose" in sys.argv
    with open(EXE, "rb") as f:
        f.seek(LOAD_IMAGE_AT)
        img = f.read(LOAD_IMAGE_END - LOAD_IMAGE_AT)

    starts = {int(r["linear"], 16) for r in csv.DictReader(
        open(os.path.join(ROOT, "ground_truth", "units.csv"), encoding="utf-8"))}

    hits = []
    i = img.find(PROLOGUE)
    while i >= 0:
        hits.append(i + 0x10000)
        i = img.find(PROLOGUE, i + 1)

    off_boundary = [h for h in hits if h not in starts]

    def ret_before(lin):
        """True if the bytes before this address end in a return."""
        back = img[lin - 0x10000 - 5: lin - 0x10000]
        for pad in range(3):                      # allow trailing padding
            end = len(back) - pad
            if end >= 3 and back[end - 3] in RET_IMM and back[end - 2:end].count(0) == 1:
                return True
            if end >= 1 and back[end - 1] in RETURNS:
                return True
        return False

    missed = [h for h in off_boundary if ret_before(h)]
    body = [h for h in off_boundary if h not in missed]

    print(f"framed prologues in the load image: {len(hits)}")
    print(f"  at a units.csv boundary:          {len(hits) - len(off_boundary)}")
    print(f"  off-boundary, after a return:     {len(missed)}  <- possible missed functions")
    print(f"  off-boundary, mid-unit:           {len(body)}  <- merged blobs, expected")

    def fmt(lin):
        seg, off = divmod(lin, 16)
        return f"{seg:04x}:{off:04x}"

    if missed:
        print("\npossible missed function starts:")
        for lin in sorted(missed):
            nxt = img[lin - 0x10000: lin - 0x10000 + 24].hex(" ")
            print(f"  {fmt(lin)}  {nxt}")
    if verbose and body:
        print("\nmid-unit prologues (merged blobs):")
        for lin in sorted(body):
            print(f"  {fmt(lin)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
