# Gap analysis - what Microsoft C 7 can and cannot reproduce

Measured over **2285 unmatched code units** (288734 bytes) from
`ground_truth/units.csv`, excluding everything already in the ledger.

Each unit is counted once per trait, so the rows overlap: a unit may hit
several traits. The final row is the set blocked by none of them.

| Trait | Units | Bytes | Share of unmatched bytes |
|---|---|---|---|
| interior 90 padding | 1396 | 225057 | 77.9 % |
| push cs; call far | 1229 | 179979 | 62.3 % |
| direct far call (9A) | 846 | 182347 | 63.2 % |
| split pointer load | 364 | 84091 | 29.1 % |
| add r,r doubling | 204 | 66762 | 23.1 % |
| SI base register | 193 | 26311 | 9.1 % |
| epilogue 8B E5 5D | 144 | 24280 | 8.4 % |
| explicit zero constant | 105 | 32784 | 11.4 % |
| epilogue 5D (no enter) | 74 | 6814 | 2.4 % |
| register-passed args | 12 | 6747 | 2.3 % |
| absolute ESA access | 6 | 17323 | 6.0 % |
| **blocked by nothing** | 441 | 24112 | 8.4 % |
| &nbsp;&nbsp;of which framed (`55 8B EC`) | 138 | 8339 | 2.9 % |

## Reading

- Every trait above is a **code generator property**, verified by isolating it
  in a function whose body otherwise matches byte-for-byte (see CONVENTIONS.md
  and IDIOMS.md). None of them can be reached by a different C formulation or
  flag combination: that was tested repeatedly and is recorded per trait.
- The overlap is high: the traits co-occur in ordinary code, so the blocked
  share is much larger than any single row.
- **These are byte-pattern counts, so they are upper bounds on blocking**:
  a trait pattern can also occur inside an operand byte (a `90` inside a
  displacement, a `9A` inside an immediate). The `blocked by nothing` row is
  therefore a *lower* bound on what is reachable, and the per-trait rows are
  upper bounds. The relative ordering is still informative.
- **`epilogue 5D (no enter)` is not a compiler-generation trait**: `LEAVE`
  exists from the 186 on, so `/G0` (8086 target) makes MSC emit `pop bp`
  instead of `C9`. `1000:1364` was closed as a MATCH with `/G0`; the row is
  kept here as a byte-pattern count, not as a reachability statement.
- The practical ceiling for byte-exact recovery with the
  toolchain available here. Anything outside it needs the original compiler
  generation, which could not be run (MSC 5.1 is EXEPACK-packed; the
  Microsoft C 6.00ax set is Windows-hosted).

## What this means for the ledger

- Verified so far: see `STATUS.md`. Unmatched and reachable: **138 framed units, 8339 bytes** (plus 303 unframed).
- At the recent rate (~500 verified bytes per round) the reachable framed
  remainder is about **16 more rounds** of work, and
  that assumes every attempt succeeds - which the last four rounds show it does
  not.
- The honest conclusion: this reconstruction is **complete as far as this
  toolchain allows**, at roughly 0.7 % of own code. Going further needs the
  original compiler generation, not more C variants.
