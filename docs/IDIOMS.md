# IDIOMS — separated per toolchain

Rule 4a of the template applies universally and is not repeated here.
After each solved diff cause, exactly the rule found goes here.

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
