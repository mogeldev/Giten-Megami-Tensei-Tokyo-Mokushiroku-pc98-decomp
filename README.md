# Giten Megami Tensei: Tokyo Mokushiroku — DDS98.EXE decompilation

Byte-exact reconstruction of the game engine **DDS98.EXE** (偽典・女神転生 ～東京黙示録～,
1997) following the workflow for byte-verified decompilation:
every function is **MATCH** (byte-identical), **RELOCS** (identical except for real
OMF linker relocations), or **PENDING** with a documented cause — nothing is faked.

## Status (2026-11-23)

- **Phase 0 complete** — original toolchain: **Microsoft C/C++ 7.0** (CL 8.00, 1992),
  compiled under dosbox-x with HDPMI (HX-DOS runtime) as DPMI server.
- Confirmed flags: **`/G1 /AM /Gs /Os`** (80186 base, medium model, no
  stack checks, size optimization) — proven on byte-identical calibration functions.
- **12 functions byte-verified** (RELOCS), 1 PENDING (jump-merge polarity,
  five tested constructs documented).
- Coverage: **66 / 306 814 code bytes (0.022%)** — the honest byte metric from
  `tools/coverage.py`, not the function count.

## Structure

```
docs/           CONVENTIONS (parameters+evidence), MATCHING (ledger), IDIOMS, PROGRESS, STATUS
ground_truth/   functions/strings/imports + foreign_crt (foreign-code signatures)
src/calib/      reconstructed sources (8.3 names — required by MSC-CL-1992)
tools/          gt (inventory), build (DOSBox-x recipe), omfdump, match, verify, coverage, markcrt
```

## Building

Requires Microsoft C/C++ 7.0 (abandonware, e.g. via archive.org) and dosbox-x +
HX-DOS runtime. The complete recipe including every pitfall is in
`docs/CONVENTIONS.md`: HDPMI32 TSR before every CL call, `-nopromptfolder`,
APPDATA redirect, 8.3 source file names, `cycles=max`.

**No original material in this repo:** the binary, the toolchain, and the raw
decompiled excerpts are deliberately kept outside — this repo contains only our
own reconstructions, tools, and documentation.
