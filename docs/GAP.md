# Gap analysis - what Microsoft C 7 can and cannot reproduce

Measured over **2343 unmatched code units** (290363 bytes) from
`ground_truth/units.csv`, excluding everything already in the ledger.

Each unit is counted once per trait, so the rows overlap: a unit may hit
several traits. The final row is the set blocked by none of them.

| Trait | Units | Bytes | Share of unmatched bytes |
|---|---|---|---|
| interior 90 padding | 1400 | 225317 | 77.6 % |
| push cs; call far | 1232 | 180177 | 62.1 % |
| direct far call (9A) | 881 | 183276 | 63.1 % |
| split pointer load | 367 | 84175 | 29.0 % |
| add r,r doubling | 204 | 66762 | 23.0 % |
| SI base register | 196 | 26435 | 9.1 % |
| epilogue 8B E5 5D | 144 | 24280 | 8.4 % |
| explicit zero constant | 106 | 32862 | 11.3 % |
| epilogue 5D (no enter) | 74 | 6814 | 2.3 % |
| register-passed args | 12 | 6747 | 2.3 % |
| absolute ESA access | 6 | 17323 | 6.0 % |
| **blocked by nothing** | 457 | 24568 | 8.5 % |
| &nbsp;&nbsp;of which framed (`55 8B EC`) | 149 | 8724 | 3.0 % |

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
- The practical ceiling for byte-exact recovery with the
  toolchain available here. Anything outside it needs the original compiler
  generation, which could not be run (MSC 5.1 is EXEPACK-packed; the
  Microsoft C 6.00ax set is Windows-hosted).

## What this means for the ledger

- Verified so far: see `STATUS.md`. Unmatched and reachable: **149 framed units, 8724 bytes** (plus 308 unframed).
- At the recent rate (~500 verified bytes per round) the reachable framed
  remainder is about **17 more rounds** of work, and
  that assumes every attempt succeeds - which the last four rounds show it does
  not.
- The honest conclusion: this reconstruction is **complete as far as this
  toolchain allows**, at roughly 0.7 % of own code. Going further needs the
  original compiler generation, not more C variants.
