# Handoff — how to add a row

Practical notes for whoever continues this. The [README](README.md) indexes the project and
[SUMMARY](SUMMARY.md) says where it stands; this is the workflow.

## Prerequisites

- `giten/DDS98/DDS98.EXE` (not tracked) for the image and the inventory;
- `toolchain/msc7i` (MS C 7.0) and DOSBox-X + HDPMI32; `toolchain/msc6c` exists but currently
  produces no object (see `GAP.md`);
- Python: `python` on PATH is a stub in this environment - use the full path.

## The loop that produced 480 rows

```powershell
python tools/dis.py <va> <length>                       # read the unit first, always
# write src/calib/<name>.c, then:
python build.py src/calib/<name>.c --flags "/G1 /AM /Gs /Os" --force
python tools/match.py <va> <symbol> --obj build/<name>.OBJ --size <bytes>
```

If `match.py` says MATCH or RELOCS, add the ledger row, then:

```powershell
python tools/verify.py --fast     # seconds; samples
python tools/verify.py            # ten minutes; does every row
python tools/checkled.py          # consistency: sizes, sources, duplicates
python tools/report.py            # regenerates docs/STATUS.md
```

If it says DIFF, the first differing byte names the wall - check `WALLS.md`
before changing the source, because most misses are a known wall rather than a
transcription error. Record the miss in `PROGRESS.md`; a documented wall is worth
more than a wrong row.

## Rules that have paid

- **`dis.py` first.** Hand-decoding produced at least three wrong conclusions.
- **Never exceed the object symbol's length** with `--size` - a longer comparison reads into the
  next function and reports a false match (round 186).
- **Rows may be shorter than their inventory window** when the window includes padding
  (rounds 174, 244 - three rows are 27 bytes inside 28-byte windows), and they may be **longer**
  when the window cuts the function short (`cutwin.py`).
- **Suspect the declaration before the compiler.** Round 238's near/far rule (a function ending
  in `ret n` whose first parameter is at `[bp+04]` is near) matched two units that had failed
  rounds earlier - one wrong attribute moves every operand by a constant.
- **Test a rule against the whole pool.** Round 197 did this and closed an avenue; round 211
  measured the doubling wall at 199 units / 66 381 bytes, which is why it is not worth more
  experiments.

## Where to look next

1. `ENTER.md` - the `C8`-framed units. Structural reason to work: MSC under `/G1` makes the same
   frame choice, so these are clear of the frame wall. Two rows came from here.
2. `BLOCKED.md` - the unmatched units by class, biggest first.
3. `pending.txt` + `src/pending/pending1.c` - 13 of the 38 PENDING rows are machine-re-testable:
   `python tools/recheck.py --sweep` retests all of them across five flag sets in about a minute.
4. `MISSING.md`/`GAP.md` - what tooling or toolchain would change the picture.

## What not to do

- Do not add a row that `verify.py` has not proved; the ledger's value is that every row is
  reproducible.
- Do not publish the game binary, the toolchain, or anything derived byte-for-byte from the image
  (`ground_truth/strings.csv` is gitignored for that reason).
- Do not "fix" a near-miss by guessing at the source until the bytes happen to line up - three
  rounds of that usually ends in a row that is right for the wrong reason.
