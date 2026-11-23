# MATCHING ledger

One line per address; size = real length ≠ 0; status `MATCH | RELOCS | PENDING`.
Always recompute counters from this file, never from memory (template phase 5).

**Note format (read by `tools/verify.py`):**
`src=<source file>; flags="<cflags>"; <free text>` — verify rebuilds each
(src, flags) combination once and then compares all associated
rows. Verification therefore does not depend on which OBJ currently sits in
`build/`. PENDING rows carry no `src=` and are not built.

| va | name | size | status | note |
|----|------|------|--------|------|
| 35ca:8090 | get0 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16 DGROUP fixup |
| 35ca:8094 | get1 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16 DGROUP fixup |
| 35ca:8098 | get2 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16 DGROUP fixup |
| 35ca:809c | get3 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16 DGROUP fixup |
| 1fd5:0006 | get_1a4 | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16 fixup (DGROUP 0x1A4) |
| 43a0:000c | get_2fce | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16 fixup (DGROUP 0x2FCE) |
| 4dce:0002 | get_2c50 | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16 fixup (DGROUP 0x2C50) |
| 4e99:000c | get_2d0c | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16 fixup (DGROUP 0x2D0C) |
| 257f:0004 | get_l | 8 | RELOCS | src=src/calib/cget3.c; flags="/G1 /AM /Gs /Os"; 2x disp16 fixup, DX:AX return (Ghidra FUN_1871_d0e4) |
| 398d:0004 | get_ln | 8 | RELOCS | src=src/calib/cget3.c; flags="/G1 /AM /Gs /Os"; __near, 2x disp16 fixup (Ghidra FUN_35ca_3c34) |
| 2131:000c | set_flag | 6 | RELOCS | src=src/calib/cflag1.c; flags="/G1 /AM /Gs /Os"; or byte [0x0F44],0x40 |
| 20b2:0000 | OR_JOIN | 14 | RELOCS | src=src/calib/cor1.c; flags="/G1 /AM /Gs /Os"; g_or \|= x (store form 09, not return 0B) |
| 20ab:000c | _wait_change | 20 | RELOCS | src=src/calib/cor1.c; flags="/G1 /AM /Gs /Os"; spin wait on volatile int (reload in loop head) |
| 4fac:000a | inc_39f8_capped | 12 | RELOCS | src=src/calib/cinc1.c; flags="/G1 /AM /Gs /Os"; if (g<0x10) g++ |
| 35ff:0004 | SET_21A4 | 13 | RELOCS | src=src/calib/coset1.c; flags="/G1 /AM /Gs /Os"; far pascal setter `g_21a4 = v` (A3 store form) |
| 3b20:0006 | SET_1764 | 13 | RELOCS | src=src/calib/coset1.c; flags="/G1 /AM /Gs /Os"; far pascal setter `g_1764 = v` |
| 4c9b:000a | SET_2C16 | 13 | RELOCS | src=src/calib/coset1.c; flags="/G1 /AM /Gs /Os"; far pascal setter `g_2c16 = v` |
| 1fc6:0004 | AND_9B2A | 14 | RELOCS | src=src/calib/coset1.c; flags="/G1 /AM /Gs /Os"; `return v & g_9b2a` (23 = and ax,[disp], result in AX — not a store) |
| 1fc7:0002 | AND_00F6 | 14 | RELOCS | src=src/calib/coset1.c; flags="/G1 /AM /Gs /Os"; `return v & g_00f6` |
| 2f22:0006 | SET_1C48 | 13 | RELOCS | src=src/calib/coset2.c; flags="/G1 /AM /Gs /Os"; far pascal setter `g_1c48 = v` (inventory size 340: Ghidra merged units) |
| 1fc8:0000 | OR_RET_F6 | 17 | RELOCS | src=src/calib/coset2.c; flags="/G1 /AM /Gs /Os"; `g_00f6 \|= v; return g_00f6` (`09 06` then `A1`) |
| 1fc8:0012 | ANDNOT_RET_F6 | 18 | RELOCS | src=src/calib/coset2.c; flags="/G1 /AM /Gs /Os"; `g_00f6 &= ~v; return g_00f6` (`F7 D0` then `21 06` then `A1`) |
| 1871:37ce | set_9b3c | 7 | RELOCS | src=src/calib/cset2.c; flags="/G1 /AM /Gs /Os"; `void __near f(void) { g_9b3c = 1; }` (`C7 06` immediate store) |
| 35ca:8df8 | get_b98ea | 6 | RELOCS | src=src/calib/cset2.c; flags="/G1 /AM /Gs /Os"; `int __far f(void) { return (unsigned char)g; }` (`A0` load + `2A E4` zero-extend) |
| 458e:a206 | reset_slot_count | 7 | RELOCS | src=src/calib/cset3.c; flags="/G1 /AM /Gs /Os"; `g_39f8 = 0` — resets the slot counter proven in rounds 17/18 |
| 458e:35ae | init_234e | 7 | RELOCS | src=src/calib/cset3.c; flags="/G1 /AM /Gs /Os"; `g_234e = 1` |
| 4df7:0002 | init_9a08 | 7 | RELOCS | src=src/calib/cset3.c; flags="/G1 /AM /Gs /Os"; `g_9a08 = 1` |
| 3db4:0006 | zero_1bac | 7 | RELOCS | src=src/calib/cset3.c; flags="/G1 /AM /Gs /Os"; `g_1bac = 0` (inventory size 40: merged blob) |
| 2603:3efc | F_3EFC | 13 | MATCH | src=src/calib/cset4.c; flags="/G1 /AM /Gs /Os"; `return d - b` with 4 word args (`retf 8`) — byte-identical, no relocation to mask |
| 458e:8306 | f_8306 | 10 | RELOCS | src=src/calib/cset4.c; flags="/G1 /AM /Gs /Os"; `int __near f(void) { return 1 << g_b9958; }` (`B8 01 00` / `8A 0E` / `D3 E0` / `C3`) |
| 35ca:8072 | @swap_78cc | 10 | RELOCS | src=src/calib/cswap1.c; flags="/G1 /AM /Gs /Ox"; `__fastcall` exchange `old = g; g = v; return old` — /Ox picks DX as temp, /Os and /Ot pick CX |
| 35ca:825a | OFF4 | 14 | MATCH | src=src/calib/cset5.c; flags="/G1 /AM /Gs /Os"; word at offset +4 of a far parameter (`C4 5E 06` les, `26 8B 47 04` es:[bx+4]); byte-identical |
| 35ca:8268 | OFF6 | 14 | MATCH | src=src/calib/cset5.c; flags="/G1 /AM /Gs /Os"; same accessor with offset +6 |
| 35ca:8d52 | OFF1 | 14 | MATCH | src=src/calib/cset5.c; flags="/G1 /AM /Gs /Os"; same accessor with offset +1 (unaligned word read) |
| 2603:53a0 | WRAP3 | 18 | MATCH | src=src/calib/cset5.c; flags="/G1 /AM /Gs /Os"; `return ((b - a) + 2) & 3` with byte parameters (`2C FE` = sub al,-2); byte-identical |
| 458e:8e08 | TEST80 | 13 | MATCH | src=src/calib/cset5.c; flags="/G1 /AM /Gs /Os"; `return v & 0x80` with byte parameter (inventory 14: trailing gap byte) |
| 2603:ccda | NEG_MINUS1 | 16 | PENDING | `return -1 - v`: original stages through DX (`8B 56 06 / 2B C2`), MSC 7 emits `2B 46 06` under /Os, /Ox, /Ot and a framed version under /Od, /O2. Three source variants (local temp, assignment-chain, `-1 + -v`) all give the memory-operand form |
| 35ca:2306 | IDX_142A | 16 | PENDING | near pascal `return g_142a[i]`; original multiplies the index with `03 DB` (add bx,bx), MSC 6 and MSC 7 emit `D1 E3` (shl) at every tested level — see the hand-ASM note in CONVENTIONS.md |
| 37ce:000c | WRAP_37CE | 12 | RELOCS | src=src/calib/cwrap1.c; flags="/G1 /AM /Gs /Os"; forwarder `push [bp+4]; call inner; retn 2` (rel16 masked) |
| 35ca:1e54 | SUB_P3_P1 | 21 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; near pascal `(p[3] - p[1]) + a`, declaration order `(int __far *p, int a)`; byte-identical |
| 35ca:1e7e | SUB_P1_P3 | 22 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; far pascal `(p[1] - p[3]) + a`; byte-identical |
| 35ca:5550 | TEST_AND | 22 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; `(*p & mask) != 0` — `cmp ax,1 / sbb ax,ax / inc ax` bool form; byte-identical |
| 35ca:8012 | @swap_reset | 21 | RELOCS | src=src/calib/cswap2.c; flags="/G1 /AM /Gs /Ox"; exchange plus three zero stores, temp in DX (per-file /Ox, inventory 22: gap byte) |
| 2603:452e | SWAP_IF_LT | 34 | MATCH | src=src/calib/cswap3.c; flags="/G1 /AM /Gs /Ox"; `if (*b < *a) { t = *a; *a = *b; *b = t; }` through two far pointers, incl. the `push ss / pop ds` after `lds`; /Os and /Ot spill the temporary and produce ENTER 2 |
| 458e:5e66 | COPY_PAIR | 35 | RELOCS | src=src/calib/cptr3.c; flags="/G1 /AM /Gs /Os"; `*a = g_2b0a[13]; *b = g_2b0a[14];` with the global far pointer loaded twice (BX reuse) |
| 4fab:000a | get_39f8_clamped | 16 | PENDING | slot index allocator (caller FUN_458e_a20e: sentinel -1, slots 0x27 B). Best variant /Ox: 14/16 B — remaining diff `C3 90` (early return + padding) vs. `EB 03` (jump merge, one ret). Tested: /Os, /Od, /O1, /O2, /Ox, /Os /Oy, ternary both polarities, if/else+local |
| 1f2d:000e | CLAMP_A | 20 | PENDING | min(max(x,1),g), __fastcall (arg in AX, bare retn), global 0x4688. Original frameless with DX temp (`8B 16 d / 3B C2 / 7E 02 / 8B C2`); MSC7 produces memory operands under /Ox (`39 06 d / 7D 03 / A1 d`), a frame under /Os. 6 variants tested |
| 1f2f:0002 | CLAMP_B | 20 | PENDING | Sibling of CLAMP_A, global 0x468A, same cause |
| 352a:0004 | reset_9b30 | 22 | PENDING | g1=0; g2=0; far call(0x18,1) — pascal, callee cleans up. MSC7: /Os|/Ot|/Ox -> `33 C0 A3 A3` (8 B, frameless); /O2 -> `C7 06` x2 (12 B, with frame). Original: C7-06 stores WITHOUT frame -> codegen generation questionable (MSC 6.x?) |
| 4527:000a | reset_9b30b | 22 | PENDING | Duplicate body of reset_9b30 (second code copy), same cause |
| 458e:a20e | SLOT_FILL | 166 | PENDING | Slot fill routine (pascal, 1 far param). Best variant 162/166 B; remaining diff: original walks the offset only in SI (no write-back of the parameter), MSC7 C writes the param/stack slot back |
| 4fad:0006 | CONV | 16 | PENDING | Lookup table[c] (word table DGROUP 0x396A, near-pascal). /Os gives everything identical except 2 B: `D1 E3` (shl bx,1) instead of `03 DB` (add bx,bx); /Ox cross-checked, unchanged |
