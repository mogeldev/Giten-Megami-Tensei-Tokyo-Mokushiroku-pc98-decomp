# Gap analysis - what Microsoft C 7 can and cannot reproduce

Measured over **2183 unmatched code units** (286798 bytes) from
`ground_truth/units.csv`, excluding everything already in the ledger.

Each unit is counted once per trait, so the rows overlap: a unit may hit
several traits. The final row is the set blocked by none of them.

| Trait | Units | Bytes | Share of unmatched bytes |
|---|---|---|---|
| interior 90 padding | 560 | 163606 | 57.0 % |
| split pointer load | 364 | 84091 | 29.3 % |
| add r,r doubling | 201 | 66460 | 23.2 % |
| SI base register | 199 | 28886 | 10.1 % |
| register-passed args | 12 | 6747 | 2.4 % |
| absolute ESA access | 4 | 17213 | 6.0 % |
| mov ax,0 explicit | 3 | 4603 | 1.6 % |
| **blocked by nothing** | 1209 | 81206 | 28.3 % |
| &nbsp;&nbsp;of which framed (`55 8B EC`) | 528 | 30943 | 10.8 % |

## Reading

- Every trait above is a **code generator property**, verified by isolating it
  in a function whose body otherwise matches byte-for-byte (see CONVENTIONS.md
  and IDIOMS.md). None of them can be reached by a different C formulation or
  flag combination: that was tested repeatedly and is recorded per trait.
- **`90 0E E8 rel16` is not a trait**: that is Microsoft LINK
  /FARCALLTRANSLATION (/F, with /PACKC) rewriting the compiler's `9A seg off`
  into NOP; PUSH CS; CALL NEAR. `tools/match.py` recognises the rewrite, so
  those call sites are stripped before classification; 3 507 of the 3 564
  `0E E8` in the image carry that NOP.
- Likewise not counted: direct `9A` far calls (ordinary output, operand is a
  relocation), the bare `5D` epilogue (that is the `/G0` 8086 target) and
  `C7 06 <g> 00 00` zero stores (MSC 6.0 emits them).
- **These are byte-pattern counts, so they are upper bounds on blocking**:
  a trait pattern can also occur inside an operand byte (a `90` inside a
  displacement, a `9A` inside an immediate). The `blocked by nothing` row is
  therefore a *lower* bound on what is reachable, and the per-trait rows are
  upper bounds. The relative ordering is still informative.
- The practical ceiling for byte-exact recovery with the
  toolchain available here. Anything outside it needs the original compiler
  generation, which could not be run (MSC 5.1 is EXEPACK-packed; the
  Microsoft C 6.00ax set is Windows-hosted).

## What this means for the ledger

- Verified so far: see `STATUS.md`. Unmatched and reachable: **528 framed units, 30943 bytes** (plus 681 unframed).
- At the recent rate (~500 verified bytes per round) the reachable framed
  remainder is about **61 more rounds** of work, and
  that assumes every attempt succeeds - which the last four rounds show it does
  not.
- The honest conclusion: this reconstruction is **complete as far as this
  toolchain allows**, at roughly 0.7 % of own code. Going further needs the
  original compiler generation, not more C variants.
## MSC 6.0 toolchains produce no object - cause found (round 67)

`toolchain/msc6i/BIN/CL.EXE` is **not a DOS program**: run under DOSBox it prints
"This program cannot be run in DOS mode." (the 16-bit Windows / NE stub message).
A header check over every CL.EXE in the tree:

| toolchain | CL.EXE size | format |
|---|---|---|
| msc7i | 71 680 | runs in DOSBox (the toolchain every verified row uses) |
| msc6i | 29 859 | **NE (16-bit Windows)** - cannot run in DOS |
| msc6b | 71 680 | PE header |
| msc6c | 81 184 | MZ/DOS, but produces no object and no CL log |
| msc51 | 31 329 | MZ but EXEPACK-packed (see the MSC 5.1 section) |

So the pre-MSC7 codegen questions cannot be answered from `msc6i`/`msc6b` at all,
and `msc6c` needs its launcher investigated.

**The original MSC 6.0 distribution is present**: `toolchain/msc6_disks/DISK1..8.IMG`
(8 x 1.2 MB floppy images). The DOS-hosted `CL.EXE`/`C1.EXE`/`C2.EXE` are almost
certainly inside; extracting them into a fresh `toolchain/msc6dos` is the concrete
next step for this line of investigation.
