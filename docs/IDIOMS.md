# IDIOMS — separated per toolchain

Rule 4a of the template applies universally and is not repeated here.
After each solved diff cause, exactly the rule found goes here.

## Round 66 - template families with wildcard displacements
- **A family is bigger than its first sightings.** Run the shape as a template with
  `(?P<d>..)` where the displacements are, and look for members whose unit size
  is the pattern length **plus padding** (`00` or `90`). Seven of the eight new
  swap-and-return members were invisible because their unit carried a trailing
  `00`; the function is 19 bytes, the unit 20.
- `tools/swapgen.py` generates a whole family from one template: extract the
  globals, emit one function per member, build once, match all. Same shape as
  `setters.py` and `wraps.py` - the pattern for any new family.
- Contrast worth remembering: the same source gives `8B 56 06 / 83 FA 63` for a
  clamp (DX staging, /Ox) but `83 7E 06 63` (memory operand) in other contexts.
  When a clamp misses, try the /Ox variants before changing the source.
## Round 70 - jump-target padding is the fourth unsteerable trait
- The original compiler **pads jump targets with `90` even in size-optimised
  code**. MSC 7's `/Os` never pads, and `/Ot` does not merely add the nops - it
  restructures returns into early exits (`mov ax,r / retf` per block). So a unit
  whose source is otherwise correct can still be 2 bytes short and out of reach.
- Symptom to recognise: displacements in every branch off by exactly 1-2, with
  `90` bytes present at the corresponding places in the original. Stop
  investigating the source once you see it - it is padding, not logic.
- Confirmed on two independent units (`47ef:0008`, `2aa3:0002`). Together with
  block order and evaluation order, that is **four** codegen choices no C variant
  or flag combination reaches.
## Round 69 - what the misses are now made of
- The remaining near-misses in the reachable set cluster into three codegen
  choices that cannot be steered from C: **branch-block order** (which arm falls
  through), **jump-target padding** (`EB 03 90` vs `EB 02`, i.e. /Os removes
  what the original has), and **operand evaluation order**.
- Recognising those three saves rounds: if the diff is only a displacement, a
  swapped block, or a swapped load, the source is already right.
- A **signed/unsigned pair** of otherwise identical units (`7F`/`77`,
  `7D`/`73`) is strong evidence that the one source with two parameter types
  is correct even when neither instance matches byte-for-byte.
## Round 68 - absolute far addressing is unavailable; two statements beat one
- **MSC 7 cannot emit `es:[disp16]`** for a far object: even with
  `MK_FP(const_seg, const_off)` it loads the segment into a register and
  addresses `es:[bx]`. Units that use absolute ESA addressing are therefore out
  of reach - this is settled by two independent attempts, stop revisiting it.
- **Split compound bit manipulation into statements.** `g = (g & M) | X;` makes
  MSC load `g` into a register; `g &= M; g |= X;` produces the memory-operand
  form `81 26 <g> M` that the binary contains. Same for `|=` after `&=`.
- A near `int` index into a far `char` pointer gives `26 C6 40 dd 00`
  (`es:[bx+si+disp]`) - that is `p[i + n] = 0` only when the index is signed
  near; a plain `char __far *p` parameter is enough.
## Round 67 - MK_FP for fixed-segment far pointers
- **`MK_FP(0x4363, off)` is how to write a far pointer whose segment is a
  constant.** Writing `(char __far *)(0x43630000L + off)` makes MSC compute the
  sum as a long and emit a spurious `cwd`; `MK_FP` yields `imul/add` for the
  offset and a plain `mov dx,0x4363`, which is what the binary contains.
- Generators must use a **prefix match** with trailing `00`/`90` allowed, and
  must record the matched length (not the unit size) in the ledger - units
  routinely carry one padding byte that is not part of the function.
## Round 65 - filter by blocking trait before transcribing
- **Build the candidate list by exclusion, not by inclusion.** Once the blocking
  traits of the other compiler generation are known, drop every unit containing
  one of them, and the match rate per attempt jumps: this round verified 8 of 8
  attempts after the filter, against roughly 1 in 4 before it.
- The four exclusions: `03 C0`-style `add r,r` doubling; `0E E8` / `9A`
  far-call forms; `8E 46` split far-pointer loads; `8B E5 5D` epilogue.
- **swap-and-return**: `int old = g; g = v; return old;` compiles to
  `8B 16 <g>` (old into DX) + `8B 46 06` + `A3 <g>` + `8B C2`, and needs
  `/Ox` - under `/Os` the temporary spills to a frame.
- `((long)b << 16) | (unsigned)a` is a 13-byte function; the giveaway is the
  reversed halves `8B 46 08 / 8B 56 06` (first argument into AX, second into DX).
## Round 64 - the dd reg,reg anomaly explained
- **bs() is an intrinsic**: with `/Oi` it expands to `99 33 C2 2B C2`
  (`cwd / xor ax,dx / sub ax,dx`), which is exactly what the binary contains.
  Without `/Oi` MSC emits a far call instead. Use `/Oi` for any function with
  `abs` in it.
- **Doubling is an instruction-selection fingerprint**: the original emits
  `03 C0` (`add ax,ax`) where MSC 7 emits `D1 E0` (`shl ax,1`). This is
  the same family as the `add bx,bx` (`03 DB`) that the round-48 census found
  and could not explain. So that anomaly is **not hand-written assembly** - it is
  this compiler's choice of `add` over `shl` for doubling. Any unit with a
  doubled index is therefore unreachable from MSC 7 by exactly two bytes.
- `/Ot` is needed for the `*5` strength reduction to appear as
  `8B D0 C1 E0 02 03 C2` (mov/shl/add) rather than `6B C0 05` (imul).
## Round 63 - two far-call encodings, one of them unavailable
- The binary contains **213 units** with `90 0E E8 <rel16>` (`push cs` then a
  near call) and **86** with `9A` (direct far call, often to an absolute
  `0000:xxxx` target). MSC 7 emits `9A` even for a far callee defined in the
  same file, and a near callee gives a bare `E8`. So the `push cs; call` form
  cannot be produced from C here - a wrapper family of 213 units is blocked on it.
- **Classify the call form before generating**: `E8` (near callee) and
  `0E E8` (unavailable) look alike at a glance; a regex that accepts both
  produces confident-looking but wrong sources.
- Pascal parameter mapping for generated wrappers: offset `n` maps to
  `p[nparams-1-(n-6)//2]`, because the first declared parameter sits at the
  highest frame offset.
## Round 62 - what a body-identical / epilogue-different function proves
- `11d8:000c` is the control experiment the fingerprint needed: 58 of 60 bytes
  match, including every store and the far-pointer return, and only the teardown
  differs (`8B E5 5D CB` vs MSC 7's `C9 CB`). No flag variant (/Os, /Ot, /Od,
  /Ox) produces `8B E5 5D`. So the epilogue difference is independent of the
  source form - it is a code generator property, not a C mistake.
- **Scheduling is not steerable**: `1e38:0002` differs only in whether the global
  or the parameter is loaded first. `register`, declaration order and expression
  order did not change it, so stop trying.
- When a mid-size function misses, check whether the body is byte-exact before
  investing in source variants: if only the epilogue or the register choice
  differs, the source is already right and the difference belongs in the
  fingerprint notes.
## Round 60 - conventions inside the sweeper
- When a generated family verifies 0 hits, suspect the **generator** before the
  binary. Three shared bugs made every `C9 CA` unit look like a source mismatch:
  `far` inferred from `CB` only (`CA` is far too), the window size excluding
  the `retf imm16` bytes, and missing `__pascal` (so `retf` instead of
  `retf 2`). A family that suddenly matches 2/2 after those fixes is the signal
  that the code was never wrong.
- **Pascal uppercases symbols**: a generated function `f_29f9_000e` is exported
  as `F_29F9_000E`, so match the uppercase name.
- `param_store` = `55 8B EC 8B 46 xx A3 <disp> C9 (CA|C2) imm16` is a fully
  mechanical family: `void __far __pascal f(int a) { g = a; }`, 13 bytes.
## Round 59 - generated sources must not collide with the ledger
- A generator that writes `src/calib/<name>.c` can silently destroy a verified
  calibration source if the name is reused. Two rules: pick generated names that
  cannot clash with hand-written ones (`cset6` was fine, `cset5` was not), and
  have the generator refuse to write a path that appears in `docs/MATCHING.md`.
- `tools/setters.py` sweeps the **store-setter shape**
  `55 8B EC (8B 46 xx A3 d)+ (C7 06 d imm)? C9 CA/C2 imm` and verified 3/3 on its
  first run - a fully mechanical family, so it should be re-run after every split
  or inventory change.
## Round 57 - callbacks with permuted arguments
- **A callback's argument order is visible in the push sequence.** With pascal and
  four parameters, `push [bp+6] / [bp+4] / [bp+8] / [bp+0xA]` means the callee
  receives `(arg3, arg4, arg2, arg1)` - i.e. the source reads
  `g_cb(c, d, b, a)`. Assuming the natural order was wrong and cost one attempt;
  reading the offsets top to bottom gives it immediately.
- **The result of an indirect call can be written back into a parameter slot**:
  `89 46 0A` (store AX into the first parameter) followed by re-reading it.
  That is `a = g_cb(...); return a;` where `a` is a parameter.
- Confirmed the LOADFIX situation for the record: this DOSBox-x build has no
  `Z:\LOADFIX` (`Bad command or filename`), and DOSBox 0.74 fares no better,
  so EXEPACK-packed compilers cannot be relocated.
## Round 56 - the EXEPACK wall
- **Every MSC 5.1 compiler binary is EXEPACK-packed** (`CL`, `C1`, `C1L`,
  `C2`, `C3`). Bypassing the driver is therefore no workaround: driving
  `C1 -> C2 -> C3` hits the same `Packed file is corrupt` error.
- The failure is silent in our harness: the redirected log file is never created,
  so it looks like the DOS shell skipped the command. Only capturing dosbox-x's
  own stderr reveals `LOG: INT 21h WRITE warning: Detected 'Packed file is
  corrupt'`. Diagnose packed-binary failures that way, not from the CL log.
- `Z:\LOADFIX` is not available in this DOSBox-x build, so the packed image
  cannot be relocated by the usual trick. Writing an EXEPACK unpacker is the
  remaining path.
- **Byte selection is another second-generation marker**: the original often
  stores AH directly (`26 88 27`) where MSC 7 copies AH to AL first
  (`8A C4 / 26 88 07`). Seen in `29ed:0004`; same family as the split pointer
  loads (`1df5:0008`, `2aa3:0048`).
## Round 54 - struct callbacks
- **Callback member at a struct offset**: `if (s->fn) s->fn(s, a, b);` with
  `fn` at `+0x10` compiles exactly as the binary shows once the struct is
  declared honestly: `les bx,[bp+8]`, null test via
  `26 8B 47 12 / 26 0B 47 10` (segment and offset of the member), then
  `push es / push bx` to pass the struct itself as the first argument and
  `26 FF 5F 10` for the indirect call.
- **Return + push order determines the signature.** `retn 8` with a far struct
  pointer plus two words means 4 + 2 + 2 bytes, and pascal pushes left to right,
  so the struct pointer must be the first declared parameter. Getting this right
  from the bytes avoids trial and error.
## Round 53 - indirect call and ternary-mask idioms
- **Far function pointer null test**: `if (fp) fp(...)` compiles to
  `A1 <seg> / 0B 06 <off> / 74 xx` (or ax,seg with ax,off) followed by
  `FF 1E <off>` - a far indirect call through the DGROUP pointer. Declare it as
  `extern void (__far __pascal *g_cb)(int, int, int);`.
- **`cond ? N : 0` with a small constant N** is a mask idiom:
  `sbb cx,cx / and cx,N`. Writing `N * (cond)` or `(cond) << n` gives
  `neg`/`shl` instead and misses. Recognise `sbb` + `and imm` as the
  ternary, not as hand-written masking.
- **Absolute ESA addressing is out of reach**: for `*(int __far *)0x48270862L`
  MSC builds the segment in a register and addresses `es:[bx]`, while targets in
  this binary use `mov ax,seg / mov es,ax / mov es:[disp16]`. Such units are
  candidates for the second compiler generation rather than for more C variants.
## Round 51 - steering the allocator, and finding twins
- **A trivial local can steer register allocation.** `*p ^= mask; return mask & *p;`
  with `mask` used directly gives `8B 46 06` (param to AX); copying it through
  a local (`int m = mask;`) plus `/Ox /Oa /Os` yields `8B 5E 06 / 8B C3` -
  the value staged in BX, exactly like the original. When the diff is only "which
  register holds the temp", try routing the value through a local before changing
  the algorithm.
- **`tools/twins.py`** finds unrecorded byte-identical twins of already verified
  functions - a free ledger row each. Run it after every batch.
- **`26 8B 07` / `26 2B 47 04`** (`es:[bx]` / `es:[bx+4]`) is plain C far
  pointer arithmetic: `(*p - p[2]) + a` with `int __far *p`.
## Round 50 - duplicates exist; scan them correctly
- **Byte-identical duplicates are real** and each one yields a free ledger row
  (one transcription, several addresses). They must be found with a correct
  terminator test: a unit ends with `CB`/`C3` at `b[-1]` **or** with
  `CA`/`C2` at `b[-3]` (the `retf imm16` opcode, not `b[-2]`). Getting
  this wrong silently hides most of the binary - it cost a false "no duplicates"
  conclusion in round 49.
- Found groups: `1df5:0008`/`1dfc:0066`, `1e1e:0046`/`1e1e:0068`,
  `43b0:0200`/`43d2:000a`, plus duplicates of two already-verified ALU helpers.
- **`int __far __pascal f(int __far *p) { return *p; }`** is 13 bytes:
  `55 8B EC C4 5E 06 26 8B 07 C9 CA 04 00` (MATCH).
- Units that keep the far pointer in `BX:ES` and never write the parameter back
  are NOT reproduced by MSC 7 (it increments the parameter in memory or spills a
  frame); that is the same second-generation codegen as the `5D` epilogue.
## Round 45 — the full flag set, and two silent failure modes
- **`/Ox /Oa /Os` is a real combination.** `/Oa` = assume no aliasing -> the
  compiler keeps a global in a register across a comparison (`8B 16 <disp>` /
  `3B C2` / `8B C2` instead of `3B 06 <disp>` / `A1 <disp>`). `/Os` placed after
  `/Ox` removes jump-target padding (`7D 04` instead of `7D 05 … 90`). Before
  declaring a diff "link-time alignment", try `/Os` after `/Ox`.
- **A failed compile can look like success**: a stale OBJ satisfies an
  "object exists?" check. `build.py` now deletes OBJ/stamp/log first, so a broken
  source fails loudly. Check the CL log whenever a source edit seems to have no
  effect.
- **`*/` inside a C comment ends it.** Writing `**/G1 /AM ...**` in prose
  terminates the block comment and the compiler reports a vanished symbol.
- **Early returns mimic unit boundaries**: terminator followed by a prologue is
  also what `if (...) return ...;` produces. A split is only valid when no short
  jump inside the block targets the candidate start.

## Round 44 — the 4-byte fastcall class, and how to grow the splitter
- **Fastcall store setter**: `void __near __fastcall f(int v) { g = v; }` is
  `A3 <disp> C3` (4 B); the far variant ends `CB`. The value arrives in AX and
  there is no prologue, so the terminator is the only clue for the model.
  **In the medium model `/AM` the default for `__fastcall` is `__far`**, so a near
  variant must say `__near` explicitly or the object ends in `CB`.
- **Growing the split rule**: measure each candidate prologue opcode (number of
  boundaries added + sample bytes) instead of adding them by intuition. `31` (xor)
  is a trap: it matches inside functions (`31 46 FE` = `xor [bp-2],ax`).
- The 4-byte getter/setter class is exhausted in this binary (dedicated sweep:
  0 getters, 2 setters left after excluding the ledger).

## Round 41 — split the inventory, and guard the window length
- **The inventory merges functions.** `tools/split.py` recovers 507 hidden units
  (2 463 real vs 1 956 entries). Split before judging progress or mining
  candidates; `mine.py --units` works on the split list.
- **A window that is too short always passes a byte comparison.** Both failure
  modes are silent: too short (narrowing cannot fail) and too long (padding that
  the object also emits). `verify.py` now requires every window to end at a
  `ret`/`retf`/`retf imm16` and rejects trailing `90` padding, naming the real
  length. Six rows were wrong before this check existed.
- **Long getters** compile to `A1 <disp>` + `8B 16 <disp+2>` + `CB` (low word in
  AX, high in DX).
- **14-bit sign extension** is `(g << 2) >> 2` → `C1 E0 02` / `C1 F8 02`.

## Round 39 — the inventory undercounts functions, and link-time alignment
- **189 inventory entries contain 2..6 real functions** (`terminator + gap +
  new prologue`). 461 units are hidden this way. Any progress metric computed
  against `ground_truth/functions.csv` therefore overstates completion; split
  blobs before judging coverage. Detection recipe is described in PROGRESS.md.
- **Wrapper families**: four siblings that differ only in a pushed constant are
  a reliable MATCH/RELOCS source — all 21 bytes each, one masked far call.
- **A lone `90` after an unconditional `jmp` is usually link-time alignment**,
  not a source difference: the label is aligned based on the unit's final image
  offset, which we cannot control from a single-object compile. Classify such a
  diff separately instead of hunting for another C variant.

## Round 36 — far-pointer algorithms
- **`lds`/`les` analyses**: a function that loads a far pointer with `lds`
  clobbers DS, so the compiler emits `push ss / pop ds` before returning. Seeing
  that pair is normal for C, not a sign of hand-written code.
- **`/Ox` decides whether a temp is spilled**: the conditional far-pointer swap
  is register-only under `/Ox` (34 B, MATCH) but spills the temporary and uses
  `ENTER 2` under `/Os` and `/Ot`. Fourth `/Ox` case in the project — when the
  original is frameless and register-only, try `/Ox` first.
- **Repeated global loads are not automatically a different source form**: the
  far pointer in COPY_PAIR is loaded twice because BX is reused for the
  destination. Register pressure explains it; no separate source variant needed.

## Round 33 - argument order, near/far, and /Ox register allocation
- **Parameter offsets prove the calling convention.** With `push bp; mov bp,sp`
  a far function has `[bp+2]` = return offset, `[bp+4]` = return segment, so
  arguments start at `[bp+6]`. `__pascal` pushes left to right, therefore
  `[bp+6]` is the **last declared** parameter and the highest offset
  (`[bp+0xC]` for four args) is the first. Reading `[bp+6] - [bp+0xA]` means
  `return d - b` for `(int a, int b, int c, int d)`.
- **The terminator names the model**: `C3` = `__near`, `CB` = `__far`,
  `CA imm16` = far with callee-pops. Never take it from the decompiler header.
- **`/Ox` can change register allocation independently of size.** The exchange
  `old = g; g = v; return old` becomes `8B 16 / A3 / 8B C2` under `/Ox`
  (temp in DX, matching the original) but `8B 0E / A3 / 8B C1` (temp in CX)
  under `/Os` and `/Ot`. When only a register differs, vary the optimization
  level before assuming a different source form.
- **MATCH is achievable for register-only functions**: `2603:3efc` has no
  memory operand at all, so there is nothing to mask; MATCH is reserved for
  exactly these.
## MS C 8.x / x86-16 real mode — **calibrated: NO**

Candidates not yet checked (record as a rule only after calibration):
- near vs far: cdecl-style stack frames (`BP`-based); MS switch `/Gc` (pascal) possible.
- Globals live in DGROUP (`DS`), startup sets `DS=0x58FC ≠ CS` → not tiny/small.
- Register choice via source form applies unchanged (extra locals instead of inline casts).
- sign/type width decide the instruction (`jg/jl` vs `ja/jb`, `movzx` equivalents).
- Set membership: OR chain vs `switch` (16-bit compilers often build linear comparison chains).

## MSC 7.0 /Os — observed idioms (calibration 2026-11-23)
- `return g;` (leaf, /Gs): bare form `A1 <disp> CB` — no ENTER, no register
  saves. The same applies to 32-bit (`A1` + `8B 16`) and near variants (`C3`).
- `g |= 0x40;`: direct `80 0E <disp> 40`.
- `if (g < K) g++;`: `83 3E <disp> K / 7D 04 / FF 06 <disp> / C3` (jge skips body).
- **Ternary trap**: `return (g < K) ? g : -1;` compiles under MSC7 /Os to the
  early-return form (two RETs) — NOT to the jump-merge form of the original
  (4fab:000a: `jl / mov ax,-1 / jmp / mov ax,[g] / ret`). A local result variable
  forces ENTER+stack slot instead. Open: which source form produces the merge
  form (candidate: expression reusing the value — check when the call-site
  context is known).

## MSC 7.0 /Os — slot routine 458e:a20e (round 17, 4 hypotheses)
- Best C result 162/166 B (v3: `*src++` walk): ENTER, or/jge,
  `e9` branch (>127 distance forces jge+3/jmp rel16 by itself),
  `imul ax,ax,0x27`, stores as `[bx+disp16]` with field offsets — everything fits.
- Open: the original walks the offset ONLY in si (never writes back); MSC7 C
  writes the parameter back on `*src++` ([bp+6]/[bp+8] stores), and with a
  local far-pointer copy the pointer gets a stack home (ENTER 16,
  LES juggling). Suspicion: source form with separate segment/offset accesses
  (FP_SEG/FP_OFF style) or inline ASM.
- Odd field/slot sizes (0x27=39): MSC7 rounds structures up — the original
  therefore uses a char array + index arithmetic, not a struct.
- `__pascal` uppercases symbol names (SLOT_FILL) and cleans up via `retf imm16`
  — the true arity can be read from the RET (here: 4 = one far pointer; Ghidra's
  'param_2' was a calling-convention artifact).

## Round 31 — the global-initializer family
- `void __far f(void) { g = <imm>; }` compiles to `C7 06 <disp> <imm16> CB`
  (7 bytes) for both `0` and `1` — the immediate store form appears whenever the
  function stores a constant and nothing else, independent of `/Os`.
- Inventory sizes around this family are one byte too long (trailing gap) or
  badly inflated for merged blobs (40 bytes for a 7-byte function) — take lengths
  from the `CB`/`C3` terminator.
- Sweep recipe that works: regex the family over the image, keep only hits whose
  offset is a known function start AND whose **linear** address is not already in
  the ledger, then compile all members in one file and match each symbol.

## Round 30 — small leaf forms confirmed
- **`void __near f(void) { g = 1; }`** → `C7 06 <disp> 01 00 C3` (7 B): MSC uses
  the immediate store for a non-zero constant even under `/Os`.
- **Byte getter** `int __far f(void) { return (unsigned char)g; }` →
  `A0 <disp>` (mov al,ds:[disp]) + `2A E4` (sub ah,ah = zero extend) + `CB`.
- **Same code, several seg:off names**: `1871:8c0c` and `2131:000c` are both
  linear `0x2131C`. Always compare linear addresses before recording a "duplicate
  function"; `verify.py` rejects the duplicate row automatically.

## Round 28 — return-form variants and length pitfalls
- **`g |= v; return g;`** compiles to `09 06 <disp>` (store) followed by
  `A1 <disp>` (reload) — 17 bytes with the `leave / retf 2` tail. The reload is
  real, not an artefact: the return value is read back from the global.
- **`g &= ~v; return g;`** gives `F7 D0` (not ax) + `21 06 <disp>` + `A1 <disp>`
  — 18 bytes. Again the long form of the return value.
- **Length must end at the `retf imm16` terminator.** A window that is one or
  two bytes short hides the tail byte(s) and still reports RELOCS — a silent
  false positive. Derive the length from the disassembled
  `leave / retf xx xx` sequence, then write it to the ledger.
- Inventory sizes are unreliable for merged blobs (seen: 340 and 214 bytes for
  a 13- and a 17-byte function). Treat them as an upper bound only.

## Round 27 — canonical one-parameter forms (byte-proven)
- **Far-pascal setter** (`void __far __pascal f(int v) { g = v; }`) compiles to
  exactly 13 bytes: `55 8B EC 8B 46 06 A3 <disp> C9 CA 02 00`. A trailing `90`
  in our object is alignment padding and lies outside the function.
- **`&`/`|` with a global**: `return v & g;` gives `23 06 <disp>` (AND r16,r/m16 —
  result in AX), while `g &= v;` gives `21 06 <disp>` (AND r/m16,r16 — store).
  Same pair as for OR (`0B` vs `09`). The opcode direction names the source form.
- **Inventory sizes can be one byte too long** when a gap byte follows a short
  function (setters: inventory 14, real 13). Always take the length from the
  disassembled boundary or the ledger, not blindly from `functions.csv`.

## Round 23 — optimization level changes the codegen CLASS (important!)
- **`/Oy` and `/Ox` remove the frame.** All previously verified functions
  were produced with `/Os` (frame remains, `push bp/mov bp,sp`); for frameless
  originals `/Os` is structurally wrong. Try `/Oy` first (removes only the
  frame pointer), then `/Ox` (maximum optimization — additionally changes
  branch/merge decisions and register allocation, but inserts `nop` padding).
- **Consequence for the workflow:** flags are to be chosen per source file, not
  globally — exactly as the template intends (phase 0, "flags per module").
- **Jump merge vs. early return is a flag/codegen trait, not a C trait:**
  the same ternary becomes early return under `/Os` (`ret` per branch) and
  merge under `/Ox` (`jmp` to one `ret`). When an original shows the merge form,
  vary the optimization level first before suspecting hand ASM.

## Address aliases (segment overlap)
The same code location can appear under several `seg:off` spellings in the
inventory: `3dd3:0000` (linear `0x3dd30`) is identical to `35ca:8090` — Ghidra
keeps both. For the ledger and coverage always take the **linear address** as
identity, otherwise the same code is counted twice. When searching for new
candidates, deduplicate linearly as well.

## Round 20 — two rules, both proven byte-wise
- **Assignment direction decides the opcode:** `g |= x;` produces `09 06 <disp>`
  (or **r/m, r** — result into the memory location), `return x | g;` produces
  `0B 06 <disp>` (or **r, r/m** — result into ax). The diff `09` vs `0B` therefore
  means "return value vs. compound assignment", not "wrong expression".
- **`volatile` prevents loop hoisting:** `while (g == s);` with a normal `int`
  lets MSC7 pull the load out of the loop head (load/store collapse, 18 B,
  degenerate cmp); with `volatile int` the reload stays in the head (20 B) and
  hits the original byte-exactly including the jump distance. For interrupt/timer
  flags, therefore always try `volatile` first — it is usually the historical
  truth, not just a trick.

## Slot subsystem: probably hand ASM (rounds 17/18, pattern thesis)
Four functions (4fab:000a allocator, 4fac:000a increment, 4fad:0006 conv,
458e:a20e filler) share codegen idioms that MSC7 /Os does not produce from C:
- jump-merge ternary form instead of early return (4fab)
- register walk without param write-back (458e:a20e)
- `add bx,bx` instead of canonical `shl bx,1` (4fad:0006) — /Od//O1//O2 use
  the MEMORY form `add bx,[bp+4]`, never the register form
Conclusion until disproved: this subsystem was built by the developers with
assembler/inline ASM — for RELOCS verification only a rewrite as __asm
(documented template-compliant) or PENDING remains there.
Positive side effect: /Os compresses leaf frames (ENTER 0,0 -> push bp/mov
bp,sp, LEAVE remains) — that frame matches the original exactly.
