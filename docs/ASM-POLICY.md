# ASM rows — policy

`docs/MATCHING.md` rows carry one of four statuses:

| status | meaning |
|---|---|
| `MATCH` | the C source compiles to exactly these bytes |
| `RELOCS` | identical except for relocation bytes (globals, call targets) |
| `ASM` | the bytes are reproduced with an **inline `__asm` block** |
| `PENDING` | source believed correct, documented bytes still differ |

## Why `ASM` exists

Microsoft C 7 provably cannot emit nine instructions/patterns that the original
compiler used (`docs/CONVENTIONS.md`). When a function is otherwise exact and differs
only in such an instruction, inline assembly lets the reconstruction be byte-verified
instead of being abandoned.

This compiler supports `__asm`, including references to C variables
(`__asm mov bx, i` compiles to `8B 5E 04`) and MASM-style memory operands
(`__asm mov ax, g_142a[bx]`). The first row using it is `35ca:2306` (IDX_142A), where
the index is scaled with `add bx,bx` and MSC emits `shl bx,1` for every C formulation
tried.

## The rule

**Inline assembly may only stand in for an instruction the compiler cannot emit.**
Every other byte in the row must be compiler output from the surrounding C. Writing a
whole function in assembly would reproduce the disassembler's output, not a
decompilation — that is not what this repository is for, and such rows must not be
added.

Practically: if a row requires more than a couple of `__asm` lines, it belongs in
`docs/GAP.md` as blocked, not in the ledger as verified.

## Counting

`ASM` rows are **byte-verified** — `tools/verify.py` rebuilds and re-matches them
exactly like any other row, so they cannot be faked. They are deliberately
**excluded from `tools/coverage.py`**, which counts only `MATCH`/`RELOCS`, because
they do not demonstrate a C reconstruction. When quoting coverage, quote the C-only
number; report `ASM` counts separately.
