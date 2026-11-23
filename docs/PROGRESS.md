# PROGRESS

## Round 37 — four near-misses documented, no new verified rows
Honest round: every candidate landed within a few bytes but none matched, so the
result is four precisely documented PENDING rows instead of forced ledger entries.
- **32-bit exchange** (`1871:5c26`, `35ca:209c`, 38 B each): the original keeps
  the old low word in BX (`8B D8` … `8B C3`); MSC 7 (/Os, /Ox, /Ot) and MSC 6
  (/Os, /Ox) all spill both halves to `[bp-4]`/`[bp-2]`. Three source variants
  (initialise at declaration, separate assignment, explicit low/high split) all
  give the spill form.
- **Bit set** (`2603:463c`, 38 B): ours is 34 B. The `cwd / and dx,7 / add / sar`
  prefix proved the source uses `n / 8`, not `n >> 3` (the latter gives 23 B).
  Remaining difference is allocation order — original loads the argument into SI
  first and orders `and bx,7` before `mov si,ax`.
- **Segment extraction** (`1871:7874`, 24 B): original gets the segment through
  `les` + `mov ax,es`; MSC reads `[bp+8]` directly and never emits the `les`.
- Conclusion recorded: these four are the first cases where the *shape* is C-like
  but the register allocation is not reproducible at any compiler level tested,
  which strengthens the hand-ASM suspicion for the affected modules.
- Ledger: 56 rows — MATCH 10, RELOCS 33, PENDING 13.

## Round 36 — far-pointer algorithms: one more MATCH, two RELOCS (43 verified)
- `2603:452e` SWAP_IF_LT (34 B) is a **MATCH** in `src/calib/cswap3.c` with
  `/G1 /AM /Gs /Ox`: `if (*b < *a) { t = *a; *a = *b; *b = t; }` through two far
  pointers, including the `push ss / pop ds` that follows the `lds`. Under /Os
  and /Ot the temporary is spilled (ENTER 2) and the frame differs — fourth
  per-file `/Ox` case.
- `458e:5e66` COPY_PAIR (35 B, RELOCS): `*a = g_2b0a[13]; *b = g_2b0a[14];`. The
  global far pointer appears loaded twice, which is simply the compiler reacting
  to BX being reused for the destination pointer — a useful reminder that a
  "redundant" reload in the original is often just register pressure.
- `35ca:8012` @swap_reset (21 B, RELOCS, `/Ox`): exchange plus three zero stores,
  temp in DX. Same family as the round-33 exchange, so the flags were predictable.
- Two length corrections again: inventory 22 -> real 21 (swap_reset) and
  36 -> real 35 (copy_pair).
- Ledger: 52 rows — **MATCH 10, RELOCS 33**, PENDING 9.

## Round 35 — three MATCHes with far-pointer arithmetic (9 MATCH rows total)
- Swept the far-pointer accessor family (word/byte accessors, far stores): only
  the three found in round 34 exist. Wrapper/thunk families are almost absent —
  exactly one forwarder in the whole image (`37ce:000c`, RELOCS).
- Three new **MATCH** rows in `src/calib/cptr2.c` (`/G1 /AM /Gs /Os`):
  `35ca:1e54` SUB_P3_P1 (21 B, near pascal `(p[3] - p[1]) + a`),
  `35ca:1e7e` SUB_P1_P3 (22 B, far variant),
  `35ca:5550` TEST_AND (22 B, `(*p & mask) != 0`, the
  `cmp ax,1 / sbb ax,ax / inc ax` bool form).
- The only diff was the **declaration order**: pascal pushes left to right, so
  the argument at `bp+4` is the last declared one. Writing `(int a, p)` produced
  the pointer at `bp+4`; `(p, a)` reproduces the original. Confirms the round-33
  rule for mixed word/pointer argument lists.
- Two more candidates skipped with reason: `2603:5306` and `1871:8b0a` scale the
  index with `03 F6`/`03 DB` (`add si,si` / `add bx,bx`), which neither MSC
  generation emits — consistent with the hand-ASM finding.
- Ledger: 49 rows — **MATCH 9, RELOCS 31**, PENDING 9.

## Round 34 — five MATCHes in one batch (73 bytes, six MATCH rows total)
- Mined the 12..22-byte band and transcribed six forms. Five are **byte-identical
  with zero relocations** (`src/calib/cset5.c`, `/G1 /AM /Gs /Os`):
  `35ca:825a` OFF4, `35ca:8268` OFF6, `35ca:8d52` OFF1 (word at +4/+6/+1 of a far
  parameter), `2603:53a0` WRAP3 (`((b - a) + 2) & 3`), `458e:8e08` TEST80 (`v & 0x80`).
- Two fixes were needed and both came straight from the byte diff:
  - the dereference must be `*(int __far *)` — with a near cast MSC emits
    `8B 5E 06` instead of `C4 5E 06` (`les`), losing the segment load;
  - byte arguments follow the same pascal rule as words: `[bp+6]` is the last
    declared one, so the subtraction order had to be flipped.
- `458e:8e08` was 13 bytes, not the inventory's 14 (trailing gap).
- **`add bx,bx` (03 DB) is never produced by MSC 6 or MSC 7** — tested /Os, /Ox,
  /Ot, /Od, /O2 on `return g_142a[i]`; all emit `D1 E3` (shl). Since the binary
  contains 74 such sites, this is now solid evidence that those functions are
  hand-written assembly, not C. Recorded in CONVENTIONS.md.
- Two new PENDINGs with full evidence: `2603:ccda` (DX staging for `-1 - v`) and
  `35ca:2306` (the array index above).
- Ledger: 45 rows — **MATCH 6, RELOCS 30**, PENDING 9.

## Round 33 — first MATCH, plus two RELOCS (31 verified)
- **`2603:3efc` F_3EFC (13 B) is the first MATCH in the project**: bytes identical
  with no relocation to mask. Form `return d - b` with four word arguments
  (`retf 8`); the pascal argument order (left to right push) puts the last
  declared parameter at `bp+6`, which is what the original reads.
- `458e:8306` f_8306 (10 B, RELOCS): `int __near f(void) { return 1 << g; }` —
  terminator `C3` proved it is a near function; the decompiler's `& 0x1f` is its
  own invention, the code shifts by the raw byte.
- `35ca:8072` @swap_78cc (10 B, RELOCS): `__fastcall` exchange. **First function
  proven to need `/Ox`**: `/Os` and `/Ot` put the temporary in `CX`, `/Ox` puts it
  in `DX` like the original. Third per-file-flags case after round 23.
- Rejected on byte comparison and recorded: `35ca:8072` under /Os (CX vs DX),
  `458e:a4c6` (ours frameless, original saves si/di).
- Ledger: 38 rows — **MATCH 1, RELOCS 30**, PENDING 7.

## Round 32 — family sweeper tool; small-function families measured as empty
- **`tools/sweep.py`** added: takes a family definition (regex + C template),
  finds every hit at a real function boundary not yet in the ledger (compared by
  linear address), writes the C, compiles once and matches all members;
  `--emit` prints ready ledger rows. Seven families are defined:
  `byte_store`, `word_inc`, `word_dec`, `byte_inc`, `word_copy`, `byte_copy`,
  `word_add_imm`.
- **Measured result: those families are effectively absent.** Raw occurrences in
  the whole image: `C6 06` 5, `FF 06` 1, `A1..A3` 2, `FF 0E`/`FE 06`/`A0..A2`/
  `83 06` 0 — and **none** starts at a function boundary. The compiler preferred
  other forms, so this vein is exhausted (recorded so it is not retried).
- Framed leaf clustering (prologue `55 8B EC`, epilogue `C9 CB/C3`, bodies
  disp-masked, 8..30 bytes): only **8** candidates remain, 8 distinct bodies,
  and all of them are CRT or interrupt-wrapper code at the image start.
- SLOT_FILL retested with `/Ox` and `/Os /Oy` after the round-23 discovery:
  `/Os` yields 162 B vs the original 166 B, but the difference is structural —
  original `ENTER 2` + saves `di`+`si`, ours `ENTER 8` + saves `si`. Stays PENDING.
- Ledger unchanged this round: 35 rows — 28 RELOCS, 7 PENDING.

## Round 31 — global-immediate family swept: 4 new RELOCS (28 total)
- `tools/mine.py` added (template phase 5, step 1: find candidates) — lists
  call-free, jump-free small functions with their decompiled body. Fixed it to
  dedupe by **linear** address, otherwise segment aliases of matched functions
  show up as candidates (seen: `1871:d0e4` = `257f:0004`).
- Swept the `C7 06 <disp> <imm16>` initializer family: 4 more RELOCS in
  `src/calib/cset3.c` — `458e:a206` (resets the slot counter proven in rounds
  17/18), `458e:35ae`, `4df7:0002`, `3db4:0006`. Two further scan hits turned out
  to be segment aliases of these (`0x48E8E`, `0x4FAE6`).
- Ledger: 35 rows — **28 RELOCS**, 7 PENDING.

## Round 30 — mining call-free bodies: 2 new RELOCS, 1 false lead caught by verify
- Wrote a mining script over the decompiled output (call-free bodies, size 5..24)
  and transcribed two leaf forms (src/calib/cset2.c, `/G1 /AM /Gs /Os`):
  - `1871:37ce` set_9b3c (7 B) — `void __near f(void) { g_9b3c = 1; }` (`C7 06` store)
  - `35ca:8df8` get_b98ea (6 B) — `int __far f(void) { return (unsigned char)g; }`
    (`A0` load + `2A E4` zero-extend)
- **verify caught a false lead**: I recorded `1871:8c0c` as a duplicate of
  `set_flag`; the duplicate-address check proved it is the same linear address
  (`0x2131C`) under a different seg:off — a segment alias, not a second function.
  Row removed; this is the round-23 alias lesson applied automatically.
- MSC 6.0 retested on the slot-allocator PENDING (/Ox, /Os, /O2): always emits a
  frame (`C8 ..`), so MSC 7.0 `/Ox` remains the best variant (14/16 B).
- Ledger: 31 rows — **24 RELOCS**, 7 PENDING.

## Round 29 — build cache implemented (verify 18.6 s -> 0.8 s)
- `build.py` writes a stamp (`flags`, toolchain dir, DPMI flag, source mtime and
  size) next to each object and skips the compile when all of it matches; `--force`
  bypasses the cache. Template phase 3 asks for exactly this.
- `verify.py` reports `CACHED` vs `built` per source file, so a stale cache can
  never pass silently — a flag or source change invalidates the stamp.
- Measured on this machine: first verify (8 source files around dosbox-x)
  **18.6 s**, cached verify **0.8 s**.
- Matching vein for the round: two-parameter canonical shapes (`retf 4`) and a
  masked-skeleton clustering over all 589 remaining candidates both produced no
  family — documented here so the next round does not repeat the dead ends.

## Round 28 — three more canonical forms matched (22 RELOCS total)
- Shape scan over real function boundaries found three further canonical
  far-pascal one-parameter units (src/calib/coset2.c, `/G1 /AM /Gs /Os`):
  - `2f22:0006` SET_1C48 (13 B) — `g_1c48 = v`
  - `1fc8:0000` OR_RET_F6 (17 B) — `g_00f6 |= v; return g_00f6`
  - `1fc8:0012` ANDNOT_RET_F6 (18 B) — `g_00f6 &= ~v; return g_00f6`
- Two measurement lessons, both recorded in `docs/IDIOMS.md`:
  1. Inventory sizes here are wildly inflated (340 and 214 bytes) because Ghidra
     merged several units into one function; the real length comes from the
     `leave / retf imm16` terminator.
  2. A window two bytes too narrow silently "passes": the last byte of the
     `retf` immediate was outside the compared range. Always include the full
     `C9 CA xx xx` sequence.
- Ledger: 29 rows — **22 RELOCS**, 7 PENDING.

## Round 27 — setter family matched: 5 new RELOCS, repo translated to English (2026-11-23)
- Targeted pattern search for the canonical far-pascal one-param form
  (`push bp / mov bp,sp / mov ax,[bp+6] / <op> / leave / retf 2`) found real C.
- **5 new RELOCS** (src/calib/coset1.c, `/G1 /AM /Gs /Os`):
  `35ff:0004`, `3b20:0006`, `4c9b:000a` (setters, 13 B) and
  `1fc6:0004`, `1fc7:0002` (AND-return functions, 14 B).
- Opcode direction mattered again: original `23 06` = `and ax,[disp]` (result in
  AX, function returns it) — writing `g &= v;` produced `21 06` (store) and failed.
- Sizing pitfall: the inventory size for the setters is 14 but the real function
  is 13 bytes (the follow-up gap byte was counted). Matching with the ledger's
  real length fixed the spurious `90 vs 00` diff.
- Whole repository rewritten to English (docs, tool docstrings/messages, source
  comments); logic, numbers and ledger notes verified unchanged (verify green,
  AST/comment-stripped diffs identical).
- Ledger: 26 rows — **19 RELOCS**, 7 PENDING.

## Round 26 — MSC 6.00ax obtained, hypothesis tested and disproved (2026-11-23)
- MSC 6.00ax fetched from archive.org (SHA1 verified), disks unpacked.
  Format is `SZ` (not `KWAJ`) — the MSC-7 `DECOMP` handles both; 34 headers +
  8 compiler passes decompressed (now under **dosbox-x**, one environment instead of two).
- `build.py` extended: `--msc-dir MSC6I` and `--no-dpmi` (MSC 6.0 is pure
  16-bit, no DOSX32/DPMI). MSC-7 default path still green (verify: 14 RELOCS).
- **Test of the hypothesis:** init family with MSC 6.0 under /Os, /Od, /Oa /Od ->
  always `33 C0 A3 A3`, i.e. identical to MSC 7.0. The assumption "game modules
  with MSC 6.x" is therefore **disproved** (documented in CONVENTIONS.md).
- Consequence: the hand/inline ASM hypothesis for the slot subsystem, clamp and
  init family as well as CONV is supported; the caller context remains the cross-check.

## Round 25 — suspicion: wrong compiler generation (phase-0 relapse) (2026-11-23)
- Init family (2x22 B: `g1=0; g2=0; far_call(0x18,1)`) fully decoded
  (pascal convention, argument order proven from push order) — but not
  matchable: /O2 gives the C7-06 stores WITH frame, /Os|/Ot|/Ox frameless WITHOUT.
- **Byte statistics of the binary** as cross-check: `add bx,bx` 74x vs `shl` 18x;
  `C7 06 .. 0000` 130x vs zero fold 32x; frame density 1184x (fits /Os).
  MSC 7.0 produces the most frequent original forms in no flag combination.
- Working hypothesis documented (CONVENTIONS): game modules possibly translated
  with **MSC 6.x**, linked against CRT 7. Before any further hand-ASM classification
  this must be checked, otherwise a toolchain assumption gets misdiagnosed as hand ASM.
- Ledger: 21 rows, 14 RELOCS, 7 PENDING.

## Round 24 — integrity hole closed: verify builds itself (2026-11-23)
- Ledger format canonicalized: every MATCH/RELOCS row carries
  `src=<source file>; flags="<cflags>"` — verify.py reads that and **recompiles
  every (src, flags) combination**, instead of relying on existing `build/*.OBJ`.
- Proof: `build/*.OBJ` deleted -> verify built all 6 source files and reported
  14/14 RELOCS ok, PENDING 5, green. Previously the same run would have checked
  against stale or foreign compilations (round-23 finding).
- `--fast` deliberately skips the rebuild (intermediate check only, never close-out).
- Duplicate and size-0 checks remain in verify (template phase 6).

## Round 23 — optimization level discovered as a codegen class (2026-11-23)
- Family scan with masked disp16: 3 groups. The largest (3dd3:0000..) is a
  **segment alias** of the already-matched getters (linearly identical to
  35ca:8090) — lesson: the linear address is the identity, otherwise double counting.
- Clamp siblings (1f2d:000e / 1f2f:0002, 2x20 B) decoded: min(max(x,1),g)
  with __fastcall and DX temp. 6 variants tested, MSC7 produces neither
  frameless+DX (original) — PENDING.
- **Main finding:** `/Oy` and `/Ox` remove the frame; all previous matches
  used `/Os`. `/Ox` brought get_39f8_clamped to 14/16 B (remaining: `C3 90` vs
  `EB 03`, i.e. early return+pad instead of jump merge). Flags are to be chosen
  per source file — recorded as a rule in IDIOMS.md.
- CONV cross-checked under /Ox: `D1 E3` remains (hand-ASM suspicion confirmed there).
- Integrity hole noted: verify.py does not rebuild, it checks the existing OBJs.

## Round 22 — report.py: STATUS.md is generated (2026-11-23)
- `tools/coverage.py` split into `compute()` (numbers) + `main()` (console output),
  so `tools/report.py` can use the same numbers without duplicate logic.
- `tools/report.py` writes `docs/STATUS.md`: ledger counters (MATCH/RELOCS/PENDING),
  PENDING list, coverage table, regions table. The hand-written part sits
  between `MANUAL-BEGIN`/`MANUAL-END` and survives every run (tested).
- Counters are therefore no longer maintained by hand — STATUS can no longer
  become stale or contradictory (the cause of the round-21 cleanup).
- verify green, coverage numbers unchanged (100 / 293 640 B = 0.034%).

## Round 21 — inventory cleaned up: 1956 code functions instead of 1970 (2026-11-23)
- `functions.csv` now carries `section=CODE|DATA`; `gt.py` sets the marking from
  `not_code.csv`, `coverage.py` counts only CODE rows as functions.
- Rows are preserved (size depends on the distance to the next function) —
  nothing is deleted, only classified. One source instead of two counting paths.
- Numbers unchanged correct: 294 603 code bytes − 963 CRT = 293 640 own bytes,
  100 verified (0.034%); function count now honestly 1 956 + 14 data.
- verify green (17 rows), no ledger entry falsely marked as DATA.

## Round 20 — two RELOCS + two new idiom rules (2026-11-23)
- OR_JOIN (20b2:0000): `void: g_or |= x` — the diff `09` vs `0B` was the
  assignment direction (or r/m,r = store vs. or r,r/m = return), not the expression.
- _wait_change (20ab:000c): spin wait on `volatile int` — without volatile MSC7
  hoists the loop load (18 B, degenerate cmp), with volatile the reload stays in the
  loop head and hits the original exactly including `74 F8` (20 B).
- verify.py now passes the **ledger size** through to match.py (--size):
  according to the template the ledger size is the real length; inventory windows that
  run into the following function (here 18 instead of 14 B) would otherwise
  falsify the comparison.
- Status: 14 RELOCS / 3 PENDING, 100 of 293 640 own code bytes (0.034%).

## Round 19 — 12 211 bytes of misinventory classified as data (2026-11-23)
- The 38 Ghidra decompilation errors sorted: 14 entries provably not
  code — CD-3F sound-driver command blocks (NMUSE/MIDE, 6-byte stride), linear
  word tables, 10.9 KB null field, ASCII string 'num err floor'.
- ground_truth/not_code.csv + coverage.py data category: metric now threefold
  honest — 293 640 own code bytes (instead of 306 814), 66 verified.
- ~24 further FAILs look like real functions (ENTER frame, parameter
  loads) — candidates for later rounds.

## Round 18 — conv decoded: 14/16 bytes, pattern thesis hand ASM (2026-11-23)
- 458e:a1ea == inc_39f8_capped (already RELOCS ✓) — 'slot_update' for free.
- 4fad:0006 (CONV, 16 B, near-pascal lookup): 5 source forms + 3 optimization
  levels — /Os matches EVERYTHING except 2 bytes (shl vs add bx,bx). Frame
  compaction (push bp/mov bp,sp instead of ENTER) confirmed in the original and reproduced.
- Pattern thesis matured: the slot subsystem (4 functions) consistently carries
  hand-ASM idioms — documented in IDIOMS.md as a working basis.

## Round 17 — slot routine: form decoded, 4 hypotheses, PENDING (2026-11-23)
- 458e:a20e (166 B, pascal, far param) fully disassembled: slot index flow,
  8 field offsets 0/2/4/9/11/13/15/19, conv CL push, retf 4 (=1 far param, Ghidra's
  param_2 was an artifact). Odd slot size 0x27 -> char array, no struct.
- Reconstruction v3 reached 162/166 B — remaining difference: register walk without
  stack write-back (MSC7 C writes the param back). PENDING with form analysis
  in IDIOMS.md; cslot1.c keeps v3 as the next starting point.
- Practical corner: __pascal uppercases symbols; >127 jump distance produces the
  jge+3/jmp form automatically (branch explanation for the 4fab:000a kinship).

## Round 16 — PENDING semantics proven (2026-11-23, evening)
- Caller of 4fab:000a found (FUN_458e_a20e): slot index allocator,
  sentinel -1 is checked, slots 0x27 bytes, array base DGROUP-relative
  (-0x6d58). Jump merge remains a hand-ASM suspicion — PENDING note deepened.
- FUN_458e_a20e itself (52 B slot fill routine) is a candidate for the
  next family round: parameters, field writes, RTC-free form.

## Round 15 — coverage separates foreign code (2026-11-23, evening)
- coverage.py shows a 'foreign CRT' column: 963 B (35 unique library signatures)
  are subtracted from the own-byte metric — percentage now against own bytes
  (66/305851 = 0.022%). The CRT share grows with further signature hits.

## Round 13 — CRT region mapped (2026-11-23)
- markcrt.py repaired: MS librarian aligns modules (padding after MODEND)
  — scan to the next THEADR; now 379/379 modules from MLIBCR.LIB.
- **35 unique CRT hits** (reloc-masked library signatures) in
  DDS98.EXE, from 10bd:0002 upward: __int86/_abs/_srand/__NMSG_WRITE/__dos_setvect …
  -> ground_truth/foreign_crt.csv. CRT lies at the start of the image (linker order).
- Open for the next session: extend coverage.py with a foreign-code column,
  report the CRT byte share separately in the honest metric.

## Round 11 — coverage.py + PENDING deepening (2026-11-23)
- get_39f8_clamped: 5 construct/opt combinations exhausted (ternary x2, if/else+r,
  /O1, /O2) — MSC7 never produces the jump-merge form from C. PENDING with
  hand/inline ASM suspicion documented; proof via caller context later.
- coverage.py built (template phase 6): bytes per 64-KiB region against the
  original inventory — the honest metric is 66/306814 bytes (0.022%).

## Round 10 — 0x39F8 pair: 1 RELOCS, 1 honest PENDING (2026-11-23)
- inc_39f8_capped (4fac:000a): RELOCS — `if (g<0x10) g++;` form exact.
- get_39f8_clamped (4fab:000a): PENDING — MSC7 /Os compiles the ternary to the
  early-return form; the original uses jump merge with one RET. Two
  hypotheses (ternary, if/else+r) documented; the third follows with caller context.
- IDIOMS.md populated with verified MSC idioms for the first time (template 4: add
  after each solved diff cause — here: the unsolved one too).
- verify: green — 13 ledger rows, RELOCS 12, PENDING 1.

## Round 9 — 32-bit getter pair + flag op: 11 RELOCS total (2026-11-23)
- cget3.c: get_l (far) + get_ln (__near) — DX:AX return, 2x disp16 fixup each,
  original 1871:d0e4 / 35ca:3c34 (Ghidra had mistyped get_l as 16-bit).
- cflag1.c: set_flag = or byte [0x0F44],0x40 — single member, range <=8 bytes
  thus fully classified (GET 8, pair 2, flag 1).
- verify: green, ledger 11 rows, 0 PENDING.

## Round 8 — GET family complete: 8/8 RELOCS (2026-11-23)
- Family scan (functions <=8 bytes by code shape): GET family has 8 members.
- Part 2 (cget2.c): four single-scalar getters on DGROUP 0x1A4/0x2FCE/0x2C50/0x2D0C —
  all four RELOCS; verify: green, ledger 8 rows, 0 PENDING.
- omfdump: compact 0x9C fixups with variable entry length (3/4 bytes, target index).

## Round 7 — phase 0 COMPLETE: 4 byte-verified functions (2026-11-23)
- **First RELOCS matches**: getter family 35ca:8090..9c (get0..get3),
  `mov ax,[disp16]; retf` — disp16 as the only masked linker fixup.
- **CFLAGS confirmed: `/G1 /AM /Gs /Os`** (medium model; /Gs = no chkstk
  prologues in the original; /Os = bare leaf form; /G1 = 186 idioms).
  Correction: earlier huge/large assumption wrong (near-data proof).
- match.py complete: OMF extraction (omfdump.py) + reloc masking + classification.
  MSC7 fixups run as compact 0x9C records (COMENT class A2 extension).
- verify.py is in place, runs green: ledger 4 rows, 4 RELOCS, 0 PENDING.
- Practical corner: CL dies silently for source files >8.3 characters (calibration source
  renamed cget.c); LINK.EXE (DOSX16) under dosbox-x so far unusable (hangs
  in all DPMI variants) — phase-6 topic.

## Round 5/6 — toolchain breakthrough (2026-11-23, 01:35)
- **MSC 7.0 (CL 8.00) compiles**: `triv1.c /G1 /AL` → 480-byte OMF object.
- Verified recipe: dosbox-x + HDPMI32 TSR (HX-DOS 2.17) + `-nopromptfolder`
  + APPDATA redirect + `cycles=max`. DOSBox 0.74: R6901/no DPMI; dosbox-x's own
  DPMI crashes with MSC7 (GitHub issue #3844).
- `build.py` switched to the recipe, verified end-to-end against itself.
- Toolchain decoration complete: 224/224 files from the KWAJ disks (DECOMP under
  DOSBox 0.74; findings: BAT without `CALL` eats the rest of the autoexec;
  background jobs leave DOSBox-0.74 children hanging — foreground runs only).

## Round 1 — 2026-11-23
- Parameter block documented and recorded in `CONVENTIONS.md` (MZ, x86-16 real mode,
  load-image/overlay geometry, MSC-8 candidate via CRT banner, entry `0x1871:0BE5`).
- Skeleton created: `include/dds98 src tests tools docs ground_truth`.
- `tools/`: `gt.py` (inventory), `disasm.py` (hexdump + Ghidra instruction dump),
  `match.py` (byte-match core with self-test; the BUILD step aborts in a controlled
  way until calibration), `ghidra_run.py` (headless starter with APPDATA sandbox workaround),
  `build.py` (stub, `TOOLCHAIN_NOT_CALIBRATED`).
- Phase-0 scans evaluated (ScanIdioms, 68 452 instructions): CPU base 80186+
  (`/G1` candidate), memory model large/huge (tendency `/AH`, DGROUP ≈ 102 KB),
  crt0 sequence at entry `0x1871:0BE5` confirms Microsoft-C-16-bit.
- Overlay analyzed: dense binary payload (~141 KB), no archive signature,
  no self-path reference — clarify via loader routines later.
- match.py self-test green (MATCH/RELOCS/DIFF core, reloc masking, length diff).
- Open: toolchain acquisition (MSC 8/MSVC 1.5x + DOSBox) — user approval needed;
  then calibration compile (phase 0) and first MATCH round.
