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
| 1fc8:0012 | ANDNOT_RET_F6 | 19 | RELOCS | src=src/calib/coset2.c; flags="/G1 /AM /Gs /Os"; `g_00f6 &= ~v; return g_00f6` (`F7 D0` then `21 06` then `A1`) |
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
| 2603:ccda | NEG_MINUS1 | 15 | PENDING | `return -1 - v;` with the value staged in DX (`8B 56 06 / 2B C2`). **Note:** the same source *does* match elsewhere - `418c:0266` (NEG1) verifies with the memory-operand form `2B 46 04` - so this unit was built differently or is not the same expression. Address is not a `units.csv` boundary; bytes measured directly |
| 37ce:000c | WRAP_37CE | 13 | RELOCS | src=src/calib/cwrap1.c; flags="/G1 /AM /Gs /Os"; forwarder `push [bp+4]; call inner; retn 2` (rel16 masked) |
| 35ca:1e54 | SUB_P3_P1 | 21 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; near pascal `(p[3] - p[1]) + a`, declaration order `(int __far *p, int a)`; byte-identical |
| 35ca:1e7e | SUB_P1_P3 | 21 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; far pascal `(p[1] - p[3]) + a`; byte-identical |
| 35ca:5550 | TEST_AND | 22 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; `(*p & mask) != 0` — `cmp ax,1 / sbb ax,ax / inc ax` bool form; byte-identical |
| 35ca:8012 | @swap_reset | 21 | RELOCS | src=src/calib/cswap2.c; flags="/G1 /AM /Gs /Ox"; exchange plus three zero stores, temp in DX (per-file /Ox, inventory 22: gap byte) |
| 2603:452e | SWAP_IF_LT | 34 | MATCH | src=src/calib/cswap3.c; flags="/G1 /AM /Gs /Ox"; `if (*b < *a) { t = *a; *a = *b; *b = t; }` through two far pointers, incl. the `push ss / pop ds` after `lds`; /Os and /Ot spill the temporary and produce ENTER 2 |
| 458e:5e66 | COPY_PAIR | 35 | RELOCS | src=src/calib/cptr3.c; flags="/G1 /AM /Gs /Os"; `*a = g_2b0a[13]; *b = g_2b0a[14];` with the global far pointer loaded twice (BX reuse) |
| 1871:5c26 | SWAP_LONG_40C0 | 38 | PENDING | `long f(long v) { long old = g; g = v; return old; }`. Original keeps the old LOW word in BX (`8B D8`/`8B C3`); MSC 7 (/Os, /Ox, /Ot) and MSC 6 (/Os, /Ox) all spill both words to [bp-4]/[bp-2]. Three source variants (init at declaration, separate assignment, low/high split) give the spill form |
| 35ca:209c | SWAP_LONG_13F6 | 38 | PENDING | Sibling of SWAP_LONG_40C0 with the long at 0x13F6/0x13F8, identical cause |
| 2603:463c | SET_BIT | 38 | PENDING | `table[n / 8] |= bit_table[n & 7];`. Ours is 34 B: MSC loads the argument into AX and moves AX->SI afterwards, the original loads into SI first (`8B 76 06 / 8B DE / 8B C6`) and orders `and bx,7` before `mov si,ax`. Division by 8 was required (the `cwd / and dx,7 / add / sar` sequence), `>> 3` gives 23 B |
| 1871:7874 | SEG_OF | 24 | PENDING | Returns the segment half of a far pointer. Original loads it with `C4 46 06` (les) + `8C C0` (mov ax,es) after initialising a local to 0; MSC reads `[bp+8]` directly (`8B 46 08`) and never emits the les. Three formulations tried |
| 458e:705a | SWAP_2C1A | 19 | RELOCS | src=src/calib/cex1.c; flags="/G1 /AM /Gs /Ox"; far pascal exchange, old value staged in DX (`8B 16` / `8B C2`); /Os and /Ot spill it into ENTER 2 |
| 458e:706e | SWAP_2C24 | 19 | RELOCS | src=src/calib/cex1.c; flags="/G1 /AM /Gs /Ox"; same shape for the word at 0x2C24 |
| 458e:7082 | _get_2c24 | 4 | RELOCS | src=src/calib/cex1.c; flags="/G1 /AM /Gs /Ox"; `return g_2c24` — `A1 <disp> CB` |
| 458e:8642 | state_to_shadow | 13 | RELOCS | src=src/calib/cex2.c; flags="/G1 /AM /Gs /Os"; `g_2c54 = g_9954; g_2c56 = g_9956;` |
| 458e:8650 | SHADOW_SET | 25 | RELOCS | src=src/calib/cex2.c; flags="/G1 /AM /Gs /Os"; far pascal three-argument setter; pascal order puts the first declared argument at `[bp+0xA]` |
| 458e:866a | shadow_to_state | 19 | RELOCS | src=src/calib/cex2.c; flags="/G1 /AM /Gs /Os"; copy back three words (`g_9958 = g_9963` as the third) |
| 31e3:000c | W_1000 | 21 | RELOCS | src=src/calib/cwrap2.c; flags="/G1 /AM /Gs /Os"; wrapper `ext(a, 0x1000, b)` — two parameter pushes, one constant, far call masked |
| 31e3:0022 | W_2000 | 21 | RELOCS | src=src/calib/cwrap2.c; flags="/G1 /AM /Gs /Os"; same wrapper with 0x2000 |
| 31e3:0038 | W_8000 | 21 | RELOCS | src=src/calib/cwrap2.c; flags="/G1 /AM /Gs /Os"; same wrapper with 0x8000 |
| 31e3:004e | W_4000 | 21 | RELOCS | src=src/calib/cwrap2.c; flags="/G1 /AM /Gs /Os"; same wrapper with 0x4000 |
| 31e3:0064 | W_COND | 32 | PENDING | `if (b == 1) f1(a); else f2(a);` — ours emits `75 0A … EB 08`, the original `75 0B … EB 09 90`. The single extra `90` after the `jmp` looks like jump-target alignment decided at link time (this unit sits at an odd image offset), not a source difference; kept PENDING until that can be proven |
| 2e01:0014 | _get_long_7bc2 | 8 | RELOCS | src=src/calib/cunit1.c; flags="/G1 /AM /Gs /Os"; long getter `return g_7bc2;` (`A1`/`8B 16`); hidden unit recovered by `tools/split.py` |
| 4a91:001e | _get_long_9973 | 8 | RELOCS | src=src/calib/cunit1.c; flags="/G1 /AM /Gs /Os"; same shape for the long at 0x9973; hidden unit |
| 477b:0028 | _sext14 | 10 | RELOCS | src=src/calib/cunit1.c; flags="/G1 /AM /Gs /Os"; `return (g_9971 << 2) >> 2;` — sign-extend a 14-bit value (`shl ax,2` / `sar ax,2`); hidden unit |
| 3eec:0058 | _copy_and_reset | 13 | RELOCS | src=src/calib/cunit1.c; flags="/G1 /AM /Gs /Os"; `g_29d0 = g_29ce; g_29c8 = -1;`; hidden unit |
| 3e24:006c | _get_1bb0 | 4 | RELOCS | src=src/calib/cunit2.c; flags="/G1 /AM /Gs /Os"; `return g_1bb0` (`A1 <disp> CB`) |
| 3e24:0070 | _inc_get_1bb0 | 8 | RELOCS | src=src/calib/cunit2.c; flags="/G1 /AM /Gs /Os"; `g_1bb0++; return g_1bb0;` (`FF 06` then `A1`) |
| 3e24:0078 | _dec_get_1bb0 | 8 | RELOCS | src=src/calib/cunit2.c; flags="/G1 /AM /Gs /Os"; `g_1bb0--; return g_1bb0;` (`FF 0E` then `A1`) |
| 20b4:0160 | _read24 | 37 | PENDING | Assembles a value from three bytes 0x0F3A/0x0F3B/0x0F3C without any runtime call: `A0`/`2B D2`/`8A E0`/`2A C0` pack g_f3C into AH, `ADD AX,CX` then `13 D2` (adc dx,dx) takes the carry out, then `8A F2`/`8A D4` move it into DH. Writing `v = (v << 8) + g;` three times calls the 32-bit shift helper (`9A …`), so the source form is different; hypothesis pending |
| 4fab:000a | get_39f8_clamped | 16 | PENDING | slot index allocator (caller FUN_458e_a20e: sentinel -1, slots 0x27 B). Best variant /Ox: 14/16 B — remaining diff `C3 90` (early return + padding) vs. `EB 03` (jump merge, one ret). Tested: /Os, /Od, /O1, /O2, /Ox, /Os /Oy, ternary both polarities, if/else+local |
| 1f2d:000e | @clamp_4688 | 20 | RELOCS | src=src/calib/cclamp3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `if (v < 1) return 1; if (v > g_4688) return g_4688; return v;` — /Oa stages the global in DX (round 45), /Os removes the jump-target padding. PENDING since round 23 |
| 1f2f:0002 | @clamp_468a | 20 | RELOCS | src=src/calib/cclamp3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; same clamp for g_468A |
| 352a:0004 | reset_9b30 | 22 | PENDING | `g_9b30 = 0; g_9b42 = 0;` then `far_call(0x18, 1)`. **Reclassified (round 87):** blocked by TWO traits - the zero stores use `C7 06 <g> 00 00` (explicit zero) and the call is a direct `9A` far call |
| 4527:000a | reset_9b30b | 22 | PENDING | duplicate body of reset_9b30 (second code copy), same two causes (explicit zero stores + `9A` far call) |
| 458e:a20e | SLOT_FILL | 166 | PENDING | Slot fill routine (pascal, 1 far param). Best variant 162/166 B; remaining diff: original walks the offset only in SI (no write-back of the parameter), MSC7 C writes the param/stack slot back |
| 4fad:0006 | IDX_142A | 16 | ASM | src=src/calib/casm4.c; flags="/G1 /AM /Gs /Os"; `g_39 6a[i]` word lookup where the original scales with `03 DB` (`add bx,bx`); byte-identical to 35ca:2306 modulo the table address, so the same inline-assembly scaling applies. **ASM row: byte-verified, not C-derived** - excluded from coverage (round 27; previously PENDING as trait 1) |
| 1ee7:0024 | f_1ee7_0024 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_4670` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 1ef8:0050 | f_1ef8_0050 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_4686` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 20b2:000e | f_20b2_000e | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_06de` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 2141:00a2 | f_2141_00a2 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_0f80` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 257d:0020 | f_257d_0020 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_13d6` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 2a04:0020 | f_2a04_0020 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_16c4` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 37f3:0054 | f_37f3_0054 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_13f4` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 3e70:00a4 | f_3e70_00a4 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_229e` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 3eec:0066 | f_3eec_0066 | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_29d0` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 3f3c:001e | f_3f3c_001e | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_2a1c` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 5026:013a | f_5026_013a | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; word getter `return g_3954` (`A1 <disp> CB`); hidden unit recovered by tools/split.py |
| 3f3c:0016 | _f_3f3c_0016 | 7 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; initialiser `g_2a1c = 0;` (`C7 06`); hidden unit |
| 3fcc:001a | _f_3fcc_001a | 7 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; initialiser `g_2a2c = 1;` (`C7 06`); hidden unit |
| 50c7:00aa | _f_50c7_00aa | 7 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; initialiser `g_408e = 1;` (`C7 06`); hidden unit |
| 37c1:001e | f_37c1_001e | 4 | MATCH | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; `int __near f(void) { return -1; }` (`B8 FF FF C3`); hidden unit |
| 473f:0036 | _far_long_const | 7 | PENDING | Returns the long 0x43A30000. Original materialises the low word with `B8 00 00` (mov ax,0); MSC 7 emits `33 C0` (xor ax,ax) under /Os, /Ot and /Ox, and the far-pointer formulation `(char __far *)0x43A30000L` gives the same xor. Kept PENDING |
| 1534:02aa | @set_near_a4 | 4 | RELOCS | src=src/calib/cunit4.c; flags="/G1 /AM /Gs /Os"; `void __near __fastcall f(int v) { g_00a4 = v; }` (`A3 <disp> C3`) |
| 25f0:013a | @set_far_409e | 4 | RELOCS | src=src/calib/cunit4.c; flags="/G1 /AM /Gs /Os"; `void __far __fastcall f(int v) { g_409e = v; }` (`A3 <disp> CB`); hidden unit |
| 159d:007b | f_15a4_000b | 4 | RELOCS | src=src/calib/swwordge.c; flags="/G1 /AM /Gs /Os"; word getter `return g_0006` (`A1 <disp> C3`); generated by tools/sweep.py |
| 1ee7:0028 | f_1ee9_0008 | 4 | RELOCS | src=src/calib/swwordge.c; flags="/G1 /AM /Gs /Os"; word getter `return g_4672` (`A1 <disp> CB`); generated by tools/sweep.py |
| 20b4:014c | calc_f3e | 19 | RELOCS | src=src/calib/cunit5.c; flags="/G1 /AM /Gs /Os"; `return (unsigned long)100 * g_f3e + g_f3d;` - `F7 26` (mul word) gives DX:AX, then `adc dx,0` after adding the byte; hidden unit recovered by tools/split.py |
| 35ca:5198 | OR_MASK | 16 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `void __far __pascal f(int __far *p, int mask) { *p |= mask; }` — `26 09 07` store form; byte-identical |
| 35ca:51a8 | ANDNOT_MASK | 18 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `*p &= ~mask;` (`F7 D0` not ax, then `26 21 07`); byte-identical |
| 2603:c476 | count_up | 18 | RELOCS | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `if (g_1cf0 > 0) g_1cf2++;` — 32-bit increment as `83 06 .. 01` + `83 16 .. 00` |
| 1000:1364 | abs_branch | 13 | MATCH | src=src/calib/cabs0.c; flags="/G0 /AM /Gs /Os"; the `5D CB` epilogue is the **8086 target**, not another compiler generation: `/G0` forbids LEAVE, so MSC emits `pop bp; retf`. The body was already exact under /G1; only the CPU flag was missing (cdecl, no pascal) |
| 35ca:804e | @exch_zero | 16 | RELOCS | src=src/calib/cexch1.c; flags="/G1 /AM /Gs /Ox"; `int __far __fastcall f(int v) { old = g_78ca; g_78ca = v; g_78cc = 0; return old; }` - DX temp requires /Ox; unit alias 3dce:000e |
| 3ded:000e | DEREF_WORD | 13 | MATCH | src=src/calib/cderf1.c; flags="/G1 /AM /Gs /Os"; `int __far __pascal f(int __far *p) { return *p; }` (`C4 5E 06` les + `26 8B 07`); byte-identical |
| 3b16:0030 | OR_MASK | 16 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; byte-identical duplicate of 35ca:5198 found by the fixed duplicate scan |
| 3b1a:0000 | ANDNOT_MASK | 18 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; byte-identical duplicate of 35ca:51a8 |
| 3aec:0000 | TEST_AND | 22 | MATCH | src=src/calib/cptr2.c; flags="/G1 /AM /Gs /Os"; unrecorded twin of 35ca:5550, found by tools/twins.py |
| 37b0:000a | SUB_P2_ADD | 20 | MATCH | src=src/calib/cfar2.c; flags="/G1 /AM /Gs /Os"; `return (*p - p[2]) + a;` (`26 8B 07` / `26 2B 47 04` / `03 46 06`); byte-identical |
| 3b1b:0002 | XOR_AND | 21 | MATCH | src=src/calib/cfar3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `*p ^= mask; return mask & *p;` with the mask copied through a local - only /Ox keeps it in BX; byte-identical |
| 37b3:0004 | STORE4 | 31 | RELOCS | src=src/calib/cstor1.c; flags="/G1 /AM /Gs /Os"; `void __far __pascal f(int a, int b, int c, int d) { g_13fa = a; g_13fc = b; g_13fe = c; g_1400 = d; }` - four immediate stores; store order in the code is source order |
| 3ae5:000a | XOR_AND | 21 | MATCH | src=src/calib/cfar3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; unrecorded twin of 3b1b:0002, found by tools/twins.py |
| 39eb:000a | CALL_CB | 29 | RELOCS | src=src/calib/cind1.c; flags="/G1 /AM /Gs /Os"; `void __near __pascal f(int a, int b, int c) { if (g_cb) g_cb(a, b, c); }` — null test on the far pointer via `A1`+`0B 06`, then `call far [disp]` |
| 49dd:0000 | TWOBITS | 30 | MATCH | src=src/calib/cbits1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `r = (*p == 0); r |= (p[2] == 0) ? 2 : 0;` — the ternary is MSC's `sbb cx,cx / and cx,2` mask idiom; byte-identical |
| 4665:0004 | CB_STRUCT | 32 | MATCH | src=src/calib/ccb1.c; flags="/G1 /AM /Gs /Os"; `if (s->fn) s->fn(s, a, b);` with the callback at struct offset 0x10 - far pointer null test via `26 8B 47 12 / 26 0B 47 10`, then `push es / push bx` for the self argument and `26 FF 5F 10` indirect call; byte-identical |
| 4737:0002 | SLOT_PTR | 32 | PENDING | `i = (v < 0 || v > 0xF) ? 0xF : v; return (char __far *)(0x43A30000L + i * 0x21F);` The original keeps i in BX and lays the guard out as `or bx,bx / jl +5 / cmp bx,0x10 / jl +3 / mov bx,0xF`, MSC 7 puts it in DX with different branch bodies (`jl +9`). Body semantics match, register and block layout do not - no flag combination reached it (/Os, /Ox, /Ox /Oa /Os) |
| 4e8e:0008 | STORE5 | 37 | RELOCS | src=src/calib/cstor2.c; flags="/G1 /AM /Gs /Os"; `void __near __pascal f(int a,int b,int c,int d,int e)` storing all five to 0x2D02..0x2D0A; source order equals store order |
| 2aa3:0048 | ZERO_Z | 38 | PENDING | Zeroes six words of a far struct in the order +6, +0, +8, +2, +0xA, +4. Original loads the pointer as `8B 5E 06` + `8E 46 08` and keeps AX=0 throughout; MSC 7 emits `les bx` and alternates AX/CX (`33 C9`), so 6 bytes differ. Same load-splitting as 1df5:0008 |
| 29ed:0004 | PUT_BE | 35 | PENDING | Writes a big-endian word then a zero byte, returns p+2. The original stores the high byte straight from AH (`26 88 27`) after `8B 46 08 / 03 46 06`, and advances the pointer with `83 C3 02`; MSC 7 copies AH to AL first (`8A C4 / 26 88 07`) and uses `8D 47 02` for the return. Body semantics match, byte-selection does not - third instance of the split-load/byte-selection family |
| 1e35:000c | CALL4 | 38 | RELOCS | src=src/calib/ccb2.c; flags="/G1 /AM /Gs /Os"; `if (g_cb) a = g_cb(c, d, b, a); return a;` - the callback receives the four arguments permuted (push order `[bp+6] [bp+4] [bp+8] [bp+0xA]`), and the result is written back into the first parameter slot (`89 46 0A`) |
| 1e14:0008 | KIND_OF | 32 | MATCH | src=src/calib/csm1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `int __far __pascal f(unsigned v) { if (v == 0) return 0; return (v > 0xFF) ? 2 : 1; }` - value staged in DX via `8B 56 06 / 0B D2`, unsigned `jbe`; byte-identical |
| 1ef8:0054 | SET_1EF8_0054 | 13 | RELOCS | src=src/calib/cset6.c; flags="/G1 /AM /Gs /Os"; generated store-setter (two stores), verified by tools/setters.py |
| 3bd6:003e | SET_3BD6_003E | 13 | RELOCS | src=src/calib/cset6.c; flags="/G1 /AM /Gs /Os"; generated store-setter (two stores) |
| 4c96:000e | SET_4C96_000E | 43 | RELOCS | src=src/calib/cset6.c; flags="/G1 /AM /Gs /Os"; generated store-setter: five parameter stores to 0x8600..0x8608 plus a `C7 06` initialiser of 0x2C0E |
| 1466:005b | f_146b_000b | 6 | RELOCS | src=src/calib/swbytest.c; flags="/G1 /AM /Gs /Os"; byte_store family (`C6 06 <disp8> <imm8> CB`) |
| 29f3:006e | F_29F9_000E | 13 | RELOCS | src=src/calib/swparams.c; flags="/G1 /AM /Gs /Os"; param_store family: `void __far __pascal f(int a) { g = a; }` |
| 3fcc:0022 | F_3FCE_0002 | 13 | RELOCS | src=src/calib/swparams.c; flags="/G1 /AM /Gs /Os"; param_store family, second unit |
| 3ded:001c | FIELD1 | 14 | MATCH | src=src/calib/cleft1.c; flags="/G1 /AM /Gs /Os"; `int __far __pascal f(int __far *p) { return p[1]; }` — accessor family with 3ded:000e; byte-identical |
| 37f9:000c | IDENT | 10 | MATCH | src=src/calib/cleft1.c; flags="/G1 /AM /Gs /Os"; `int __near __pascal f(int a) { return a; }` — near frame puts the argument at bp+4; byte-identical |
| 11d8:000c | SET4 | 41 | PENDING | `struct S4 *__far f(int a,int b,int c,int d)` storing three words plus `d & 0x7FFF` into a 4-int near struct and returning `(struct S4 __far *)&g_s4`. **Real length is 41, not 60** - the inventory window swallowed the next function's `00`/`56 57`; the old note's "58/60" counted that tail. Under `/G0 /AM /Gs /Os` the body matches byte-for-byte (`/G0` is the correct 8086 flag, see abs_branch); the only remaining diff is the redundant `8B E5` (mov sp,bp) before `5D CB`, which MSC 7, MSC 6 and MSC 5.1 all omit because SP already equals BP. Kept PENDING for that 2-byte teardown |
| 1e38:0002 | RECORD_CFG | 56 | PENDING | Saves `g_40ba` in DX, stores two arguments, records a code (`(c == -1) ? 7 : c` when `c != 0`), sets a flag and returns the saved word. With /Ox /Oa /Os every instruction matches **except the order of the first two**: original `8B 16 <g> / 8B 5E 06` (global first, then parameter), MSC emits the parameter load first. Scheduling difference only |
| 465d:0000 | UPD | 60 | PENDING | `if (s) { if (x != -1) s->t->x = x; if (y != -1) s->t->y = y; }` through a far pointer member at struct +4. Original keeps the struct offset in SI and the inner pointer in DI (`57 56` + `8E 46 0C` + `26 C4 7C 04`); MSC 7 uses BX and `les` with no save/restore. Same register-choice family as 1df5:0008 / 2aa3:0048 |
| 23ee:0008 | W_23EE_0008 | 46 | RELOCS | src=src/calib/cwraps.c; flags="/G1 /AM /Gs /Os"; generated wrapper, 12 pushed arguments relayed to a near pascal callee |
| 256e:000a | W_256E_000A | 22 | RELOCS | src=src/calib/cwraps.c; flags="/G1 /AM /Gs /Os"; generated wrapper, 4 arguments |
| 257d:000a | W_257D_000A | 22 | RELOCS | src=src/calib/cwraps.c; flags="/G1 /AM /Gs /Os"; generated wrapper, 4 arguments |
| 39dc:000a | W_39DC_000A | 27 | RELOCS | src=src/calib/cwraps.c; flags="/G1 /AM /Gs /Os"; generated wrapper, 6 pushed arguments including a zero constant |
| 4e11:007e | WEIGHT2 | 40 | PENDING | `return 2*(5*(abs(a)+1) + abs(b)) + c;` with `abs` as an intrinsic (/Oi). Everything matches under `/Ot /Oi` except the final doubling: original `03 C0` (add ax,ax), MSC 7 emits `D1 E0` (shl ax,1). **This is the same instruction-selection family as the `add bx,bx` anomaly (idx_142a, round 48)** - the second-generation compiler doubles with add, MSC 7 with shl. Two bytes apart, semantics identical |
| 418c:0266 | NEG1 | 13 | MATCH | src=src/calib/creach1.c; flags="/G1 /AM /Gs /Os"; `int __near __pascal f(int v) { return -1 - v; }` - the memory-operand form `2B 46 04` that MSC does emit (contrast NEG_MINUS1); byte-identical |
| 1dc0:0006 | PACK2 | 13 | MATCH | src=src/calib/creach1.c; flags="/G1 /AM /Gs /Os"; `long __far __pascal f(int a, int b) { return ((long)b << 16) \| (unsigned)a; }` — `8B 46 08 / 8B 56 06` gives the swapped halves; byte-identical |
| 3e97:0004 | STORE_AT1 | 17 | MATCH | src=src/calib/creach1.c; flags="/G1 /AM /Gs /Os"; unaligned word store at far_pointer + 1: `*(int __far *)(p + 1) = v;` — byte-identical |
| 30c7:0076 | STORE2 | 19 | RELOCS | src=src/calib/creach1.c; flags="/G1 /AM /Gs /Os"; `void __near __pascal f(int a, int b) { g_1cd0 = a; g_1cd2 = b; }` — near pascal, so `retn 4` |
| 3220:0006 | XCHG_1CEA | 19 | RELOCS | src=src/calib/cxchg1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `int old = g; g = v; return old;` — the old value is kept in DX (`8B 16 <g>`), needs /Ox |
| 34dc:0004 | XCHG_1D52 | 19 | RELOCS | src=src/calib/cxchg1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; same swap-and-return family, global 0x1D52 |
| 3f3c:0002 | XCHG_2A28 | 19 | RELOCS | src=src/calib/cxchg1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; same swap-and-return family, global 0x2A28 |
| 1e88:004a | XCHG_417C | 19 | RELOCS | src=src/calib/cxchg1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; same swap-and-return family, global 0x417C |
| 375d:0008 | X_375D_0008 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 37b3:00d0 | X_37B3_00D0 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, near variant (argument at bp+4) |
| 3d51:0006 | X_3D51_0006 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 3e5b:0002 | X_3E5B_0002 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 42ab:0006 | X_42AB_0006 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 48d6:011a | X_48D6_011A | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 4dcc:000e | X_4DCC_000E | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 4df5:000e | X_4DF5_000E | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; swap-and-return, generated |
| 47ea:000a | CLAMP63 | 20 | MATCH | src=src/calib/carith2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `if (v > 0x63) v = 0x63; return v;` - value staged in DX; byte-identical |
| 4384:000c | MASKBYTE | 20 | RELOCS | src=src/calib/carith2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `g_8670[i*4 + 1] & 0x7F` - stride-4 byte array |
| 4342:001c | ADDR4 | 18 | RELOCS | src=src/calib/carr1.c; flags="/G1 /AM /Gs /Os"; `return (char __far *)&g_866e[i * 2];` — array base into AX, DS into DX |
| 4342:0004 | SEXT11 | 23 | RELOCS | src=src/calib/carr1.c; flags="/G1 /AM /Gs /Os"; `return (g_866e[i * 2] << 5) >> 5;` — `C1 E0 05 / C1 F8 05` sign-extends the low 11 bits |
| 37a6:0016 | REC6 | 17 | MATCH | src=src/calib/carr1.c; flags="/G1 /AM /Gs /Os"; `return MK_FP(0x4363, i * 0x1E + 6);` — MK_FP with a constant segment gives `imul/add` for the offset plus `mov dx,0x4363`; byte-identical |
| 4977:0006 | CLEAR_AT | 20 | MATCH | src=src/calib/cmisc1.c; flags="/G1 /AM /Gs /Os"; `p[i + 5] = 0;` for a far char pointer with a near int index — `26 C6 40 05 00` (es:[bx+si+5]); byte-identical |
| 2e01:001c | MIX_LONG | 23 | RELOCS | src=src/calib/cmisc1.c; flags="/G1 /AM /Gs /Os"; two statements `g &= 0x3FC0; g |= (v >> 16) & 0xC03F;` produce the memory-operand `81 26 <g> C0 3F` that the single-expression form does not |
| 4a91:0002 | KEEP_PTR | 27 | MATCH | src=src/calib/cbranch1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `char __far *f(char __far *p) { if (!p) return 0; return p; }` - the null test is `or ax,bx` over both words of the far pointer; byte-identical |
| 37ad:000c | SPAN8 | 23 | MATCH | src=src/calib/cnb1.c; flags="/G1 /AM /Gs /Os"; `return ((p[2] - p[0]) << 3) + a;` for a far int pointer and a near pascal frame; byte-identical |
| 3eb3:000a | PLUS20 | 16 | RELOCS | src=src/calib/ccall1.c; flags="/G1 /AM /Gs /Os"; `return HELP_A(a) + 0x14;` — near-call wrapper with arithmetic on the result |
| 355a:000e | NESTED | 17 | RELOCS | src=src/calib/ccall1.c; flags="/G1 /AM /Gs /Os"; `return HELP_B(HELP_A(a));` — nested near calls, the result of the first pushed for the second |
| 3725:0048 | CLEAR_BIT1 | 20 | RELOCS | src=src/calib/ccall1.c; flags="/G1 /AM /Gs /Os"; `*p &= ~1; HELP_V(); return 1;` — bit clear on a far byte followed by a void call |
| 4e2e:000a | CALL_A | 20 | RELOCS | src=src/calib/cds1.c; flags="/G1 /AM /Gs /Os"; `HELP(&g_2c82, a, b)` — a DGROUP far pointer pushed first as `1E 68 <off>` |
| 4e31:0006 | CALL_B | 20 | RELOCS | src=src/calib/cds1.c; flags="/G1 /AM /Gs /Os"; same call shape, second DGROUP object |
| 218c:0002 | TWO_CALLS | 18 | RELOCS | src=src/calib/cds1.c; flags="/G1 /AM /Gs /Os"; `HELP_A(-1); return HELP_B(a);` — result of the first call discarded |
| 39dc:0026 | SIX_ARGS | 27 | RELOCS | src=src/calib/cds1.c; flags="/G1 /AM /Gs /Os"; six pushes including a constant in the middle: `HELP6(p0,p1,p2,p3,1,p4)` |
| 21f4:0000 | MUL_THEN_CALL | 23 | RELOCS | src=src/calib/cmul1.c; flags="/G1 /AM /Gs /Os"; `return HELP(a, b, d * c);` with unsigned operands - `F7 66` is the unsigned MUL, `int` gives `F7 6E` (IMUL) |
| 4e8e:0070 | _five_neg | 14 | RELOCS | src=src/calib/cfive1.c; flags="/G1 /AM /Gs /Os"; `HELP5(-1,-1,-1,-1,-1)` - five constant arguments to a near pascal callee. **This function is not a unit boundary**: units.csv merges it with the 65-byte function before it (splitter missed the `6A` prologue), so the ledger here is finer than the inventory |
| 20b4:0004 | _spin_wait | 8 | RELOCS | src=src/calib/cspin1.c; flags="/G1 /AM /Gs /Os"; `while (g_6e4 != 0) ;` - an empty spin loop is just `83 3E <g> 00 / 75 F9 / CB`; the loop polarity names the condition |
| 1f6f:000c | PICK_PTR | 44 | RELOCS | src=src/calib/cpick1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; three-way far-pointer selector `if (kind == 0) return g_a; if (kind == 2) return g_b; return g_c;` - each pointer is loaded as `A1 <off>` + `8B 16 <seg>` (offset and segment separately), and the globals must be declared in memory order 0x46EC a, 0x46F0 c, 0x46F4 b |
| 1e3b:00f0 | PICK_FLAG | 29 | RELOCS | src=src/calib/cpick2.c; flags="/G1 /AM /Gs /Os"; `if (flag == 0) return g_pa; return g_pb;` - two-way far-pointer selector. Here the parameter is compared in memory (`83 7E 06 00`), so /Os is correct; PICK_PTR needed /Ox. Which form applies is visible in the bytes |
| 37fb:0006 | CHAIN16 | 24 | RELOCS | src=src/calib/cchain1.c; flags="/G1 /AM /Gs /Os"; `SINK(*(int __far *)((char __far *)WHERE(a) + 0x16))` - near pascal (retn 2, so the argument is at bp+4) |
| 382c:0002 | CHAIN04 | 24 | RELOCS | src=src/calib/cchain1.c; flags="/G1 /AM /Gs /Os"; same chain, far pascal, field 0x04 |
| 3842:0008 | CHAIN1A | 24 | RELOCS | src=src/calib/cchain1.c; flags="/G1 /AM /Gs /Os"; same chain, field 0x1A |
| 3844:0000 | CHAIN1C | 24 | RELOCS | src=src/calib/cchain1.c; flags="/G1 /AM /Gs /Os"; same chain, field 0x1C |
| 21fb:000e | FIVE_ZEROS | 23 | RELOCS | src=src/calib/cmix2.c; flags="/G1 /AM /Gs /Os"; `HELP5(a, 0, 0, 0, 0); return 0;` - near pascal, four `6A 00` zero pushes |
| 4e2d:0002 | DGROUP_CALL | 24 | RELOCS | src=src/calib/cmix2.c; flags="/G1 /AM /Gs /Os"; `HELP(&g_2c82, a, b, c)` with a char argument - near pascal, DGROUP pointer pushed as `1E 68 <off>` |
| 4e2f:000e | DGROUP_CALL2 | 24 | RELOCS | src=src/calib/cmix2.c; flags="/G1 /AM /Gs /Os"; same shape, second DGROUP object |
| 4dae:0002 | NESTED4 | 25 | RELOCS | src=src/calib/cnest1.c; flags="/G1 /AM /Gs /Os"; `HELP2(HELP1(z, 0, x, y))` - four arguments to the inner call, result pushed for the outer one |
| 4e6f:0006 | NESTED_PTR | 26 | RELOCS | src=src/calib/cnest1.c; flags="/G1 /AM /Gs /Os"; `SINK3(WHERE0(0), 0x1F, v & 0x7F)` - a far pointer returned by the inner call is pushed as two words (`52 50` = push dx; push ax) |
| 4e71:0000 | NESTED_PTR2 | 26 | RELOCS | src=src/calib/cnest1.c; flags="/G1 /AM /Gs /Os"; same shape with a different inner helper and constant |
| 23d7:0000 | BIG_CALL | 41 | RELOCS | src=src/calib/cs32.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; `HELP12(a,b,c,d,e, 0,0,0,0, 0x4F, 0x18F, f)` - six parameters relayed plus six constants; `retf 12` fixes the argument count, and the constant run in the middle is why 12 pushes exceed 6 arguments |
| 3d1a:0008 | ADD_200 | 23 | RELOCS | src=src/calib/ccomb1.c; flags="/G1 /AM /Gs /Os"; `HELP3(a + 0x200, b, c)` - the constant is applied with `80 C4 02` (add ah,2), the tell for a +0x200 on a word |
| 4f89:0008 | _six_calls | 15 | RELOCS | src=src/calib/cloop2.c; flags="/G1 /AM /Gs /Os"; `register int i; for (i = 0; i < 6; i++) HELP(i);` - the `register` keyword puts the loop counter in **SI** (`33 F6` / `46` / `83 FE 06` / `7C F6`), which is what the binary does; without it MSC spills the counter to a frame |
| 3807:0004 | UPD_FP (dup 1/3) | 28 | PENDING | `*p = HELP(*p)` through a far pointer built from a seg/off pair. Original loads it split: `8B 76 04` + `8E 46 06` + `26 FF 34`; MSC emits `les`/`8E C1` (trait 3). Three-way duplicate group with 380c:0000 and 3811:0004 - one transcription would cover all three if the load were reachable |
| 380c:0000 | UPD_FP (dup 2/3) | 28 | PENDING | byte-identical to 3807:0004, same split-load cause |
| 3811:0004 | UPD_FP (dup 3/3) | 28 | PENDING | byte-identical to 3807:0004, same split-load cause |
| 35ca:2306 | IDX_142A | 16 | ASM | src=src/calib/casm4.c; flags="/G1 /AM /Gs /Os"; `g_142a[i]` where the original scales with `03 DB` (`add bx,bx`). Microsoft C 7 emits `D1 E3` for every formulation tried (traits table row 1), so the two scaling instructions are inline assembly. **ASM row: byte-verified, not C-derived** - excluded from coverage |
| 3d59:000c | RELAY2 | 16 | RELOCS | src=src/calib/crelay2.c; flags="/G1 /AM /Gs /Os"; `NEXT(a, b)` - and note this is **not a units.csv boundary**: the splitter recorded a fragment at 3d59:000e, the real function starts two bytes earlier, directly after the previous function's `retf` plus one padding byte. Found by `tools/framecheck.py` |
| 1fb1:0006 | SWAP_00C8 | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; returns the old DGROUP word at 0x00C8 and stores the argument; inventory window is 62 bytes |
| 3bd6:001a | SWAP_192C | 19 | RELOCS | src=src/calib/cswap4.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; same form for DGROUP 0x192C; inventory window is 36 bytes |
| 4e23:0006 | SCALE64 | 20 | MATCH | src=src/calib/calu2.c; flags="/G1 /AM /Gs /Os"; near Pascal `(b << 6) + a`; compound shift on a register local keeps the shift in SI before moving the result to AX |
| 489a:000a | CLASSIFY | 32 | MATCH | src=src/calib/calu3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; two early returns for `n <= -42` and `n >= 42`, then zero; `/Ox` stages both comparisons in DX |
| 4e8e:007e | _relay_globals5 | 26 | RELOCS | src=src/calib/cpick3.c; flags="/G1 /AM /Gs /Os"; far cdecl wrapper for a near Pascal call; first byte global passes as `int`, second as `unsigned char` |
| 4e8e:0098 | RELAY_GLOBALS | 35 | RELOCS | src=src/calib/cpick3.c; flags="/G1 /AM /Gs /Os"; far Pascal sibling appends its own argument; 36-byte inventory includes one padding byte |
| 4e8e:002e | COMPARE_CONFIG | 65 | RELOCS | src=src/calib/ccmp2.c; flags="/G1 /AM /Gs /Os"; near Pascal compares four words and an optional fifth; 80-byte inventory also contains padding and the next wrapper |
| 46e1:005c | _return_one | 4 | MATCH | src=src/calib/cret1.c; flags="/G1 /AM /Gs /Os"; near helper returning 1, directly called from `469e:0000`; 84-byte inventory window extends past its `ret` |
| 218a:0008 | _relay_minus_one | 6 | RELOCS | src=src/calib/cwrap3.c; flags="/G1 /AM /Gs /Os"; frameless far wrapper passes `-1` to a near Pascal callee |
| 4e45:0000 | _relay_defaults | 15 | RELOCS | src=src/calib/cwrap3.c; flags="/G1 /AM /Gs /Os"; frameless near wrapper passes `0, 0, 63, 63, 255`; the last constant needs a word immediate |
| 477b:0032 | SWAP_VALUE | 33 | RELOCS | src=src/calib/cbit2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; replace the low signed 14-bit field, preserve the high two bits, and return the sign-extended old value |
| 4b23:000c | STORE_IF | 31 | RELOCS | src=src/calib/cbit2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; skip either store when its argument is `-1`; a local copy stages the first value in DX while the second is compared in memory |
| 4369:0084 | APPLY_COUNT | 49 | RELOCS | src=src/calib/cbit3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; compare the signed 11-bit key in a four-byte table entry, conditionally subtract a helper result, then forward the key and adjusted count |
| 4332:000c | TAKE_COUNTS | 59 | RELOCS | src=src/calib/cbit3.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; walk the packed table backward, reducing the count for matching signed keys and stopping when the count becomes nonpositive |
| 42b9:0064 | _clear_entries | 21 | RELOCS | src=src/calib/ctable2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; mark all 64 packed entries empty and zero their counts; starts after the preceding routine and its padding inside a merged inventory window |
| 439c:0006 | TABLE_RELAY_A | 23 | RELOCS | src=src/calib/ctrelay.c; flags="/G1 /AM /Gs /Os"; hold the first argument in SI for the inner lookup and forward its result with the second argument |
| 439d:000e | TABLE_RELAY_B | 23 | RELOCS | src=src/calib/ctrelay.c; flags="/G1 /AM /Gs /Os"; same register staging and nested-call shape with different targets |
| 42ac:002c | DISPATCH | 31 | RELOCS | src=src/calib/ctry1.c; flags="/G1 /AM /Gs /Os"; keep the argument in SI across the initial call, then dispatch based on its `-1` sentinel |
| 21ff:0004 | PREP_RELAY | 31 | RELOCS | src=src/calib/cbatch1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; keep the first argument in SI and reuse it in two near Pascal calls |
| 4dac:0000 | SETUP_RELAY | 33 | RELOCS | src=src/calib/cbatch1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; pass the first call's AX result and the saved index in DX to a near fastcall callee |
| 42bc:000c | _get_entries | 6 | RELOCS | src=src/calib/ctable2.c; flags="/G1 /AM /Gs /Ox /Oa /Os"; return a far pointer to the table at DGROUP:0x876E; starts after a return and padding, outside the inventory's unit starts |
| 4386:0024 | SCAN64_A | 31 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; subtract the far Pascal scan result from 64 for the four-byte table at DGROUP:0x866E |
| 4386:0044 | SCAN64_B | 31 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; same 64-entry wrapper with the alternate scanner |
| 43ac:0004 | SCAN16_A | 31 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; 16-entry counterpart using DGROUP:0x886E |
| 43ac:0024 | SCAN16_B | 31 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; 16-entry counterpart with the alternate scanner |
| 2e31:0006 | SCAN512_A | 32 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; 512 one-byte entries at DGROUP:0x79E2 |
| 2e33:0006 | SCAN512_B | 32 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; same byte table with the alternate scanner |
| 2e35:0006 | SCAN256_A | 34 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; 256 four-byte entries at fixed far address 4827:08E6; both pointer words match without masking |
| 2e37:0008 | SCAN256_B | 34 | RELOCS | src=src/calib/ctrel2.c; flags="/G1 /AM /Gs /Os"; same fixed-address table with the alternate scanner |
| 1e1a:0002 | RELAY_22FC | 18 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of two words |
| 2b63:000c | RELAY_92BC | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; near Pascal relay of one word |
| 2b8d:0006 | RELAY_92E4 | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; near Pascal relay of one word |
| 2b8e:0006 | RELAY_9326 | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; near Pascal relay of one word |
| 31eb:0004 | RELAY_26DE | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of one word |
| 31f6:0066 | RELAY_27B8 | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of one word |
| 31f6:008c | RELAY_27FE | 15 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of one word |
| 3aa9:0002 | RELAY_AE58 | 18 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of two words |
| 4957:000e | RELAY_474A | 21 | RELOCS | src=src/calib/cfrelay.c; flags="/G1 /AM /Gs /Os"; far Pascal relay of three words |
| 1f30:0006 | RELAY_0C7E | 22 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; prepend DGROUP:0x468C to two arguments |
| 30ea:000e | _relay_7aa8_10 | 10 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; near relay of constants 1 and 10 |
| 3616:000e | RELAY_0CD2 | 22 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; append DGROUP:0x7D8E; body ends before the rest of the merged 85-byte inventory window |
| 3df1:0006 | RELAY_161E | 19 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; append DGROUP:0x79CE to a word |
| 41da:000a | _relay_7aa8_70 | 10 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; far relay of constants 1 and 70 |
| 41e9:0000 | _relay_9326_global | 10 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; relay the word at DGROUP:0x2F52 |
| 4642:002a | RELAY_62F8 | 26 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; prepend two DGROUP words to the two caller arguments |
| 4e22:000a | _relay_91c4 | 11 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; near relay of constants 0 and 4096 |
| 4f54:0070 | RELAY_4718 | 19 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; prepend DGROUP:0x860E to a word |
| 5096:000a | _relay_4f64 | 14 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; pass DGROUP:0x3970 and two zero words |
| 307b:000c | _save_01a4 | 11 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; call far Pascal with zero and store the result at DGROUP:0x1CD4 |
| 4182:000c | _save_883e | 9 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; call a far no-argument routine and save AX at DGROUP:0x85F4 |
| 4183:0006 | _use_85f4 | 9 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; load DGROUP:0x85F4 into AX for a far fastcall |
| 3220:00a2 | RELAY_80A0 | 15 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; forward a far Pascal stack argument in AX to a far fastcall |
| 36e7:020e | _save_883e_7f92 | 9 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; save the same far call's result to DGROUP:0x7F92; starts inside a merged inventory unit |
| 36e7:0218 | _use_7f92 | 9 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; reload DGROUP:0x7F92 into AX for the companion far fastcall |
| 31bc:0004 | _relay_8410 | 8 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; pass 7 to a far Pascal callee; direct call targets corroborate the entry inside a merged inventory window |
| 3b21:0004 | _relay_if_clear | 15 | RELOCS | src=src/calib/cfrly2.c; flags="/G1 /AM /Gs /Os"; call the far Pascal helper with 1 only when DGROUP:0x1764 is zero |
| 4c96:0006 | F_4C96 | 7 | RELOCS | src=src/calib/cgate1.c; flags="/G1 /AM /Gs /Os"; `return g_2c14 = 1;` - the 1 is staged in AX and stored with `A3` (disp16 fixup), no explicit-zero or `C7 06` form |
| 1aa1:0130 | F_1AA1 | 11 | RELOCS | src=src/calib/cfar6.c; flags="/G0 /AM /Gs /Os"; msc=MSC6C; nodpmi; MSC 6 /G0 pushes the long constant as `mov ax,0x800 / cwd / push dx / push ax` (/G1 uses push-immediate, MSC 7 calls through `9A`); same-segment far callee in the same file gives `0E E8` (rel16 masked). inventory 12 B incl. one trailing `90`; unit `FUN_1871_2300_u304` inside a merged Ghidra function, call target 1aa1:FECF is not a unit boundary |
| 3dcd:000a | F_3DCD_A | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78c8 + 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3dcd:0014 | F_3DCD_14 | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78c8 - 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3dcf:000e | F_3DCF_E | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78ca + 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3dcf:0018 | F_3DCF_18 | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78ca - 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3dd1:000c | F_3DD1_C | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78cc + 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3dd1:0016 | F_3DD1_16 | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; g_78cc - 1 forwarded in AX to a far fastcall; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3ea8:0008 | F_3EA8 | 8 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn psub(14) - constant pushed for a far Pascal callee; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 8 |
| 3ea9:0000 | F_3EA9 | 8 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn psub(0) - second member of the constant-relay pair; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 8 |
| 2e68:0006 | F_2E68 | 6 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn fnone() - frameless 6-byte relay; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 6 |
| 3bd6:0006 | F_3BD6 | 6 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn fnone() - frameless 6-byte relay; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 6 |
| 3dd5:0002 | F_3DD5 | 6 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn fnone() - frameless 6-byte relay; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 6 |
| 3e3f:0002 | F_3E3F | 6 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; 
eturn fnone() - frameless 6-byte relay; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 6 |
| 3d94:004a | F_3D94 | 10 | RELOCS | src=src/calib/cfarl.c; flags="/G1 /AM /Gs /Os"; near relay 
eturn psub(g_78c4); one push [disp16] then the translated call; image `90 0E E8` is LINK /FARCALLTRANSLATION of the object's `9A` (5-byte slot masked, see CONVENTIONS.md); inventory size 10 |
| 3bd6:000c | F_3BD6_C | 13 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `if (g_192c == 0) none();` - conditional frameless relay; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 3d94:0002 | F_3D94_2 | 13 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `return g_78c4 = sub2(5, 2);` - two constants then the call, result stored via `A3`; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 322b:0002 | F_322B | 14 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `return sub2(g_1cee, g_1cec);` - both arguments pushed from DGROUP; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 4e6d:000a | F_4E6D | 14 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `return sub2(g_9954, g_9956);` - sibling of 322b:0002 at different globals; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 3baa:0006 | F_3BAA | 14 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `return sub3(g_17d2, 0, 0);` - the far pointer goes through `1E 68 <disp>` (push ds; push offset), then two zero pushes; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 3309:0008 | F_3309 | 12 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; `return h(none());` - translated call first, then `push ax` into a direct `9A` callee; image `90 0E E8` = LINK /F translation of the object's `9A` (5-byte slot masked) |
| 1e16:0008 | F_1E16 | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; two far-Pascal arguments relayed, result returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 201b:0008 | F_201B | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1e16:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 21ba:000c | F_21BA | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1e16:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2df1:0008 | F_2DF1 | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1e16:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3c04:000a | F_3C04 | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1e16:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4692:0002 | F_4692 | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1e16:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1dfc:00e8 | F_1DFC | 17 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; `(a, 1)` relay; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1e56:0050 | F_1E56 | 17 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1dfc:00e8; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4daf:0058 | F_4DAF | 17 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 1dfc:00e8; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2214:000a | F_2214 | 15 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; single-argument relay; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 349a:017a | F_349A | 15 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 2214:000a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 37a6:0006 | F_37A6 | 15 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; sibling of 2214:000a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3895:0008 | F_3895 | 18 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; call result times the second argument (`F7 6E 06` after the call); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 418c:01dc | F_418C | 9 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; constant forwarded in AX to a far fastcall; inventory size 10 includes one trailing `00`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3390:025a | F_3390 | 12 | RELOCS | src=src/calib/crelay3.c; flags="/G1 /AM /Gs /Os"; call for side effect, then `return -3`; the call site is the first fixup above offset 255; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a89:0004 | F_3A89 | 12 | RELOCS | src=src/calib/crelay5.c; flags="/G1 /AM /Gs /Ox"; `return sub() != 0;` in a near function - `cmp ax,1 / sbb ax,ax / inc ax`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a8a:0000 | F_3A8A | 12 | RELOCS | src=src/calib/crelay5.c; flags="/G1 /AM /Gs /Ox"; sibling of 3a89:0004 with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3dcc:0008 | F_3DCC | 18 | RELOCS | src=src/calib/crelay5.c; flags="/G1 /AM /Gs /Ox"; far fastcall reset: old value in DX, store the argument, zero two words, return the old value; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1e0f:0008 | F_1E0F_0008 | 17 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1f45:0112 | F_1F45_0112 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 1, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 21b9:000c | F_21B9_000C | 15 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 21bb:000e | F_21BB_000E | 21 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2213:000a | F_2213_000A | 15 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2214:001a | F_2214_001A | 15 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2404:0000 | F_2404_0000 | 24 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2, p3)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a03:0002 | F_2A03_0002 | 24 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2, p3)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a04:000a | F_2A04_000A | 21 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a07:0004 | F_2A07_0004 | 28 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, -1, -32767, 0, 32767)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a09:0000 | F_2A09_0000 | 26 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 0, 0, 0, -1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2df2:000a | F_2DF2_000A | 21 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2dfe:0008 | F_2DFE_0008 | 20 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2dff:000c | F_2DFF_000C | 20 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 0)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2e01:0000 | F_2E01_0000 | 20 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, -1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3ae7:0028 | F_3AE7_0028 | 20 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3aea:000c | F_3AEA_000C | 20 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3afb:000c | F_3AFB_000C | 23 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, p2, 1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 480a:0008 | F_480A_0008 | 15 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 499f:000c | F_499F_000C | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 15, 32)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a1:0002 | F_49A1_0002 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 21, 6)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a2:0008 | F_49A2_0008 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 25, 13)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a3:000e | F_49A3_000E | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 29, 30)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a5:0004 | F_49A5_0004 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 14, 18)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a6:000a | F_49A6_000A | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 15, 32)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a8:0000 | F_49A8_0000 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 21, 6)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49a9:0006 | F_49A9_0006 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 25, 13)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49aa:000c | F_49AA_000C | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 29, 30)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49ac:0002 | F_49AC_0002 | 22 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, p1, 14, 18)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4a44:000a | F_4A44_000A | 17 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, -1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4daf:006a | F_4DAF_006A | 17 | RELOCS | src=src/calib/crely7.c; flags="/G1 /AM /Gs /Os"; relay `Sub(p0, -1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 330d:000e | F_330D | 12 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `return h(sub());` - first call's result pushed into a second translated call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2d91:000e | F_2D91 | 15 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; call, char-returning call sign-extended (`98`), stored with `A3` and returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 20b3:0002 | F_20B3 | 17 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; two calls, then `g_06e4 = 1` (`C7 06 <g> 01 00`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 218a:000e | F_218A | 20 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; near Pascal call with -1, then a far Pascal relay of the argument; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 39f8:0002 | F_39F8 | 20 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `b - sub(a)` - `sub ax,[bp+6]` then `neg ax`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31d3:0022 | F_31D3 | 21 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `return h2(sub1(a));` - result forwarded through `push ax`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31f6:0076 | F_31F6 | 21 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 31d3:0022; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 34b7:0006 | F_34B7 | 21 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 31d3:0022; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4e86:000e | F_4E86 | 21 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `sub2(b, c) - a` with the Pascal slot order; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 47c1:0006 | F_47C1 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `sub1(c + b + a)` - three adds in slot order; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4956:0008 | F_4956 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; `sub3(a, b, g)` where `g` is a DGROUP far pointer pushed as `1E 68 <disp>`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4961:0006 | F_4961 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 4956:0008 (second DGROUP far pointer); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4965:000c | F_4965 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 4956:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4967:0002 | F_4967 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 4956:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4968:0008 | F_4968 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 4956:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4969:000e | F_4969 | 22 | RELOCS | src=src/calib/crelay8.c; flags="/G1 /AM /Gs /Os"; sibling of 4956:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 20f4:000e | F_20F4 | 17 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; two call results OR-ed; /Ox stages the first in SI (`8B F0` / `0B C6`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a13:000e | F_2A13 | 17 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; `(unsigned char)sub(a)` - `2A E4` zero-extends the call result; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2341:0008 | F_2341 | 20 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; near Pascal with a `register` parameter: SI keeps `a` across the call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 37ec:0026 | F_37EC | 21 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; `sub2(a, 0x8000); return -1;` - imm16 push, then `B8 FF FF`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3816:0002 | F_3816 | 22 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; far Pascal call then a near Pascal call, both from SI; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1e55:000a | F_1E55 | 20 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; 32-bit product forwarded as a long: `F7 66` (MUL, unsigned) not `F7 6E`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3dd4:0000 | F_3DD4 | 17 | RELOCS | src=src/calib/crelay9.c; flags="/G1 /AM /Gs /Ox"; fastcall: SI keeps the AX argument across two far fastcall relays; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31e2:0004 | F_31E2 | 24 | RELOCS | src=src/calib/crelay10.c; flags="/G1 /AM /Gs /Os"; `return h(sub2(a, b));` - result forwarded through `push ax`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 37ea:0008 | F_37EA | 30 | RELOCS | src=src/calib/crelay10.c; flags="/G1 /AM /Gs /Os"; `if (x == -1) x = sub2(y, z); return x;` - store-back into the argument slot; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4e9a:0000 | F_4E9A | 24 | RELOCS | src=src/calib/crelay11.c; flags="/G1 /AM /Gs /Ox"; call first, result kept in SI, argument stored with `A3`, SI value returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31f3:0022 | F_31F3 | 26 | RELOCS | src=src/calib/crelay11.c; flags="/G1 /AM /Gs /Ox"; `register` parameter: SI feeds both the relay and the two-argument call, then is popped; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31f6:009c | F_31F6_9C | 21 | RELOCS | src=src/calib/crelay12.c; flags="/G1 /AM /Gs /Os"; `return h(sub(a));` without the SI staging (the sibling 32da:000c needs /Ox); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3e44:000e | F_3E44 | 26 | RELOCS | src=src/calib/crelay12.c; flags="/G1 /AM /Gs /Os"; `if (g != -1) { sub(g); g = -1; } return g;` - `C7 06 <g> FF FF` immediate store; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3e19:0064 | F_3E19 | 31 | RELOCS | src=src/calib/crelay12.c; flags="/G1 /AM /Gs /Os"; `sub4(3, 0, 0, -1); return h2(a, b);` - constant pushes then a second translated call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 103a:0000 | F_103A | 27 | RELOCS | src=src/calib/crelay13.c; flags="/G0 /AM /Gs /Os"; cdecl push chain; `33 C0 50` is /G0's zero-constant push and `8B E5 5D` its epilogue for functions with a call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 20ad:0000 | F_20AD | 24 | RELOCS | src=src/calib/crelay14.c; flags="/G1 /AM /Gs /Ot"; rotated `while (n) { sub(); n--; }`: test first, one alignment `90` before the call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 13c6:0000 | F_13C6 | 39 | RELOCS | src=src/calib/crelay15.c; flags="/G0 /AM /Gs /Os"; flag cell set around a long-returning call (`83 EC 04` local, `83 E5 5D` epilogue); the call is a **folded** same-segment far call: image `0E E8 rel16` (4 B) where the object has `9A` (5 B) |
| 4c96:003a | F_4C96_3A | 32 | RELOCS | src=src/calib/crelay16.c; flags="/G1 /AM /Gs /Os"; three parameter stores (`A3 <g>` in declaration order) then `sub1(1)`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 22fe:0000 | F_22FE | 42 | RELOCS | src=src/calib/crelay17.c; flags="/G1 /AM /Ox"; `register` parameter kept in SI feeds four near-Pascal calls with descending constants and one far call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 372a:003a | F_372A | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; a long from one call forwarded to the next (`52 50`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 372f:0000 | F_372F | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 372a:003a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4727:00ec | F_4727 | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 372a:003a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4a95:000e | F_4A95 | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 372a:003a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4aa2:000c | F_4AA2 | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 372a:003a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4ab1:0006 | F_4AB1 | 22 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 372a:003a; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 473f:003e | F_473F | 28 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; three-argument long relay; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a57:0002 | F_3A57 | 24 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; `return h(sub2(a, b))` - result forwarded through `push ax`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 49f2:000e | F_49F2 | 24 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; sibling of 3a57:0002; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2d52:0006 | F_2D52 | 23 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; `return sub3(sub0(), a, 0)` - leading no-argument call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2e55:0024 | F_2E55 | 23 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; `sub0(); return sub2(a, b);`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a58:000a | F_3A58 | 25 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; far result feeds a near-Pascal callee, so the second call stays `E8`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2160:0006 | F_2160 | 31 | RELOCS | src=src/calib/crelay19.c; flags="/G1 /AM /Gs /Ox"; swap-and-return around two calls; /Ox keeps the old value in SI; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2b91:0072 | F_2B91 | 30 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; `if (sub1(0)) return 0; return sub1(a);` - early-out guard; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 388b:0008 | F_388B | 30 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; `register` parameter in SI feeding two relays of the Pascal argument order; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 38b7:0008 | F_38B7 | 24 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; call for effect, then the same argument relayed again (register parameter in SI); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a18:000e | F_3A18 | 24 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; sibling of 38b7:0008; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4a41:0022 | F_4A41 | 24 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; `return h(sub(a));` with the argument kept in SI; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 4e72:0022 | F_4E72_22 | 24 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; `return sub3(sub0(), a, b);` - a no-argument call ahead of the real one; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a6f:00c2 | F_3A6F | 26 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; `sub(a); return sub2(a, 1);`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31cf:0026 | F_31CF_26 | 30 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; `h(sub(a)); return sub3(a);` - a result forwarded, then the argument relayed; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31d3:0056 | F_31D3_56 | 30 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; sibling of 31cf:0026; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31f6:0048 | F_31F6_48 | 29 | RELOCS | src=src/calib/crelay20.c; flags="/G1 /AM /Gs /Os"; `sub1(a); sub0(); return sub3(a);` - three calls, the last one not /F-translated; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3e19:0044 | F_3E19_0044 | 31 | RELOCS | src=src/calib/cshape1.c; flags="/G1 /AM /Gs /Os"; two-call relay generated by tools/shapes.py: `Sub4(3, 0, 0, -1); return Sub2(p0, p1);`; image `90 0E E8` = LINK /F translation |
| 2d49:0016 | F_2D49_16 | 29 | RELOCS | src=src/calib/crelay21.c; flags="/G1 /AM /Gs /Os"; `return d3(c3(1, 100, 0), a, 0);` - a constant-argument call nested as the first argument |
| 31cf:0008 | F_31CF_08 | 29 | RELOCS | src=src/calib/crelay21.c; flags="/G1 /AM /Gs /Os"; `return l3((long)l2(c0(), a));` - the int result widened with `cwd` and pushed as a long |
| 439f:0006 | F_439F | 22 | RELOCS | src=src/calib/crelay21.c; flags="/G1 /AM /Gs /Os"; `return ff(nf(a));` - near-Pascal callee (stays `E8`) nested into a far-Pascal callee; image `90 0E E8` = LINK /F translation of the outer `9A` |
| 3e19:0024 | F_3E19_24 | 31 | RELOCS | src=src/calib/crelay23.c; flags="/G1 /AM /Gs /Os"; three fastcall relays from a framed Pascal function (`B8 0D 00` then parameter loads); image `90 0E E8` = LINK /F translation |
| 2e39:000a | F_2E39 | 33 | RELOCS | src=src/calib/crelay23.c; flags="/G1 /AM /Gs /Os"; two far-pointer stores of zero-extended char results (`2A E4` + `C4 5E` + `26 89 07`); image `90 0E E8` = LINK /F translation |
| 2d9b:0058 | F_2D9B_58 | 35 | RELOCS | src=src/calib/crelay22.c; flags="/G1 /AM /Gs /Os"; `g_1be8 += g_1bec` as add/adc between two calls |
| 2d9b:007c | F_2D9B_7C | 35 | RELOCS | src=src/calib/crelay22.c; flags="/G1 /AM /Gs /Os"; sub/sbb sibling |
| 2d9b:00a0 | F_2D9B_A0 | 35 | RELOCS | src=src/calib/crelay22.c; flags="/G1 /AM /Gs /Os"; and/and sibling |
| 31f3:0000 | F_31F3_00 | 33 | RELOCS | src=src/calib/crelay24.c; flags="/G1 /AM /Gs /Ox"; a two-argument call, a relay of its result, then a two-argument call with a zero - SI keeps the parameter |
| 4a41:0000 | F_4A41_00 | 33 | RELOCS | src=src/calib/crelay24.c; flags="/G1 /AM /Gs /Ox"; `r = fc1(a); fc2(a, b); return r;` - DI keeps `a`, SI keeps the first result |
| 36e7:0042 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:006c | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:0096 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:00c0 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:00ea | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:0114 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; four parameters relayed, then `fc3(g_21c6, c, 1)` (DGROUP far pointer as `1E 68 <disp>`), then `c` returned; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2d49:004a | F_2D49_4A | 38 | RELOCS | src=src/calib/crelay26.c; flags="/G1 /AM /Gs /Os"; `fc3(1 - h(fc1(fc0())), a, 0)` - `1 - x` is `48 F7 D8` (dec/neg); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2d50:0000 | F_2D49_4A | 38 | RELOCS | src=src/calib/crelay26.c; flags="/G1 /AM /Gs /Os"; sibling of 2d49:004a with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a3f:008c | F_3A3F_8C | 38 | RELOCS | src=src/calib/crelay26.c; flags="/G1 /AM /Gs /Os"; `nn(fc1(fc4(a, a, b, c)), d)` - a four-argument relay forwarded through a near-Pascal call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 48ad:0008 | F_48AD | 38 | RELOCS | src=src/calib/crelay26.c; flags="/G1 /AM /Gs /Os"; guarded store: `if (!g_234c) { if (a || g_234e) fc0(); g_234e = 0; }`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1ec4:0100 | F_1EC4 | 37 | RELOCS | src=src/calib/crelay27.c; flags="/G1 /AM /Gs /Os"; `if (fc0()) { fc1(1); fc2(a, b); return -1; }` - the implicit fall-through return keeps AX; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3a3f:0066 | F_3A3F_66 | 37 | RELOCS | src=src/calib/crelay27.c; flags="/G1 /AM /Gs /Os"; `fc1(fc1(fc4(a, a, b, c)))` - a six-word call forwarded through two one-argument relays; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2d97:001e | F_2D97_1E | 36 | RELOCS | src=src/calib/crelay27.c; flags="/G1 /AM /Gs /Os"; `fc3(g_1bee, g_1bec, 0x1BE8);` - the third argument is a constant pushed with `68`, between a relay and a no-argument call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:013e | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; sibling of 36e7:0042 with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:0168 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; sibling of 36e7:0042 with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 36e7:0192 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; sibling of 36e7:0042 with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1f57:0008 | F_1F57 | 60 | RELOCS | src=src/calib/crelay28.c; flags="/G1 /AM /Gs /Os"; `long f(long v, int n)` with two branches calling `lfc(v, -n)` / `lfc(v, n)`; two distinct callees are required because a single callee makes MSC merge the sequences into a tail jump; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 1f5b:0004 | F_1F57 | 60 | RELOCS | src=src/calib/crelay28.c; flags="/G1 /AM /Gs /Os"; sibling of 1f57:0008 with a different call target; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2a45:000a | F_2A45 | 43 | RELOCS | src=src/calib/crelay29.c; flags="/G1 /AM /Gs /Os"; `fc1l(fc4(a, b, c, d))` - four ints widened with `cwd` into longs; the first callee returns long so no `cwd` follows it; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 50c4:0004 | F_50C4 | 45 | RELOCS | src=src/calib/crelay29.c; flags="/G1 /AM /Gs /Os"; `t = h1(fc1(a)); return t - h1(fc1(b));` - the temporary must be `register` to stay in SI, otherwise the argument order and staging change; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 33c1:0006 | F_33C1 | 48 | RELOCS | src=src/calib/crelay30.c; flags="/G1 /AM /Gs /Os"; `h4(h3(c2(c1(-1), a))); return h5(1);` - five calls in a long chain; `h4`'s result is discarded by making it a separate statement, and the wrapper returns `int` (a `long` return inserts `cwd`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 33c4:0006 | F_33C1 | 48 | RELOCS | src=src/calib/crelay30.c; flags="/G1 /AM /Gs /Os"; sibling of 33c1:0006 with different call targets; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 48aa:0008 | F_48AA | 47 | RELOCS | src=src/calib/crelay30.c; flags="/G1 /AM /Gs /Os"; same guard as 48ad:0008 but the body calls twice (`fc0()` then `fc2(0, 1)`), which shifts the `75 21` skip; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 2e55:003c | F_2E55 | 23 | RELOCS | src=src/calib/crelay18.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 31d3:0004 | F_31CF_08 | 29 | RELOCS | src=src/calib/crelay21.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 31d3:0038 | F_31CF_08 | 29 | RELOCS | src=src/calib/crelay21.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 36e7:01bc | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 1270:000c | F_1270_C | 1 | MATCH | src=src/calib/crelay31.c; flags="/G1 /AM /Gs /Os"; an empty far function - exactly one byte `CB` |
| 1534:02a5 | F_1534G | 5 | RELOCS | src=src/calib/crelay31.c; flags="/G1 /AM /Gs /Os"; `return g_0004;` - the byte global is read with the moffs form `A0 <disp>` and sign-extended (`98`); the function must be `__near` so the return is `C3` |
| 48d6:010a | F_48D6 | 16 | RELOCS | src=src/calib/crelay31.c; flags="/G1 /AM /Gs /Os"; `g_234a = -1; fsub(g_9b40);` - immediate store then a global pushed into a far call that stays `9A` in the image |
| 3e4f:008c | F_3E4F | 54 | RELOCS | src=src/calib/crelay32.c; flags="/G1 /AM /Gs /Os"; `fc0(); t = h1(1); h5(a, b, g_1bba); h3(t); return fc2(c, 0);` - the temp is assigned *after* a discarded call, and three pushes belong to one three-argument call; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 31f6:000c | F_31F6_0C | 59 | RELOCS | src=src/calib/crelay32.c; flags="/G1 /AM /Gs /Os"; eight calls in a row with `register int a`: `fc3(h1b(a, a)); h2(a, 2); h1(a); h4(a, 3); fc0(); return fc3(0);`; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3b72:0002 | F_3B72 | 61 | RELOCS | src=src/calib/crelay33.c; flags="/G1 /AM /Gs /Os"; `r = fc4(a, b, c, d); fc4b(g_17d2, c, 1); if (r) { h1(1); h2(); } return c;` - third parameter is `register`, DGROUP far pointer argument as `1E 68`, and the branch follows both calls; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3b6e:0002 | F_3B6E | 64 | RELOCS | src=src/calib/crelay33.c; flags="/G1 /AM /Gs /Os"; sibling whose second branch passes a constant to a `__fastcall` callee (`B8 24 00` then the call, no push); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 416b:0006 | F_416B | 58 | RELOCS | src=src/calib/crelay34.c; flags="/G1 /AM /Gs /Os"; six-iteration loop: `d = fc0()`, then `if (h1(i) >= 0 && (flags & 0x20)) { fc2(-1 - i, 0); d++; }`; two `register` locals - the index ends in SI, the counter in DI (`47`/`46`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3d94:0010 | F_3D94 | 58 | RELOCS | src=src/calib/crelay34.c; flags="/G1 /AM /Gs /Os"; `h1(g_78c4); h2(g_78c4, 0, 0); h5(g_78c4, a, b, 0x400, 1); h1(g_78c4);` in a near-Pascal function (`C9 C2 04 00`); the constant 0x400 is pushed with imm16; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 505f:000e | F_505F | 62 | RELOCS | src=src/calib/crelay35.c; flags="/G1 /AM /Gs /Os"; counter guard in a near-Pascal function: `t = n + g_395e; if (p3(1, 0x64, 2) > t) { g_395e++; if (fc(4) != -1) g_395e++; return 0; } g_395e = 0; return 1;` - arguments are pushed left to right, so the literal order shows in the bytes; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 509a:0042 | F_509A | 41 | RELOCS | src=src/calib/crelay37.c; flags="/G1 /AM /Gs /Os"; `fc4(a, b, c, d); fc3(g_3970, c, 0); return c;` - the 36e7 shape with a zero constant instead of one; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3d99:0004 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; eighth member of the 36e7 family (DGROUP far pointer at `1B1A`); identical shape to 36e7:0042; image `90 0E E8` = LINK /F translation of the object's `9A` |
| 416f:0042 | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; ninth member of the 36e7 family (DGROUP far pointer at `2A88`); image `90 0E E8` = LINK /F translation of the object's `9A` |
| 3b5e:0008 | F_3BAA | 14 | RELOCS | src=src/calib/cfarl2.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 416f:006c | F_36E7 | 41 | RELOCS | src=src/calib/crelay25.c; flags="/G1 /AM /Gs /Os"; byte-identical to a verified sibling modulo call targets |
| 3238:009c | _get_l | 8 | RELOCS | src=src/calib/cget3.c; flags="/G1 /AM /Gs /Os"; reuses a calibration probe shape (confirmed by match.py) |
| 3e34:0044 | _init_234e | 7 | RELOCS | src=src/calib/cset3.c; flags="/G1 /AM /Gs /Os"; reuses a calibration probe shape (confirmed by match.py) |
