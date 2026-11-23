# attic — unattested calibration sources

These files are the best source attempts for units that are **not** verified: they
are not referenced by `docs/MATCHING.md`, so `tools/verify.py` does not rebuild
them and they carry no claim of correctness. They are kept because each one records
what a PENDING row or a documented trait actually looks like when compiled with
Microsoft C 7 — useful when revisiting a family, useless as evidence.

Rule for this directory: a file may only be **moved out** of it by adding a ledger
row whose `src=` points back into `src/calib/` and whose `verify.py` check passes.
Nothing here is part of the verified reconstruction.

Notable contents:
- `cabs1.c`, `cclamp1.c`, `cset7.c`, `cmid1.c`, `cptr5.c`, `cslot1.c`, `cglob1.c`,
  `cwhere1.c`, `cwhere2.c` — attempts that stop on the documented codegen traits
  (epilogue, register choice, instruction order); see `docs/CONVENTIONS.md`.
- `cbe1.c` (PUT_BE byte selection), `cbyte2.c` (zero-extension order), `cbit1.c`,
  `cconv1.c`, `cidx1.c`, `cinit1.c` — near misses from the early idiom rounds.
- `m0.c`, `triv1.c` — trivial probes used while calibrating the toolchain itself.
