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
| 4fad:0006 | CONV | 16 | PENDING | `table[c]` word lookup at DGROUP 0x396A. **Reclassified (round 87):** the original indexes with `03 DB` (`add bx,bx`), i.e. trait 1 (doubling by add). Not fixable from C |
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
| 37c1:001e | f_37c1_001e | 4 | RELOCS | src=src/calib/cunit3.c; flags="/G1 /AM /Gs /Os"; `int __near f(void) { return -1; }` (`B8 FF FF C3`); hidden unit |
| 473f:0036 | _far_long_const | 7 | PENDING | Returns the long 0x43A30000. Original materialises the low word with `B8 00 00` (mov ax,0); MSC 7 emits `33 C0` (xor ax,ax) under /Os, /Ot and /Ox, and the far-pointer formulation `(char __far *)0x43A30000L` gives the same xor. Kept PENDING |
| 1534:02aa | @set_near_a4 | 4 | RELOCS | src=src/calib/cunit4.c; flags="/G1 /AM /Gs /Os"; `void __near __fastcall f(int v) { g_00a4 = v; }` (`A3 <disp> C3`) |
| 25f0:013a | @set_far_409e | 4 | RELOCS | src=src/calib/cunit4.c; flags="/G1 /AM /Gs /Os"; `void __far __fastcall f(int v) { g_409e = v; }` (`A3 <disp> CB`); hidden unit |
| 159d:007b | f_15a4_000b | 4 | RELOCS | src=src/calib/swwordge.c; flags="/G1 /AM /Gs /Os"; word getter `return g_0006` (`A1 <disp> C3`); generated by tools/sweep.py |
| 1ee7:0028 | f_1ee9_0008 | 4 | RELOCS | src=src/calib/swwordge.c; flags="/G1 /AM /Gs /Os"; word getter `return g_4672` (`A1 <disp> CB`); generated by tools/sweep.py |
| 20b4:014c | calc_f3e | 19 | RELOCS | src=src/calib/cunit5.c; flags="/G1 /AM /Gs /Os"; `return (unsigned long)100 * g_f3e + g_f3d;` - `F7 26` (mul word) gives DX:AX, then `adc dx,0` after adding the byte; hidden unit recovered by tools/split.py |
| 35ca:5198 | OR_MASK | 16 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `void __far __pascal f(int __far *p, int mask) { *p |= mask; }` — `26 09 07` store form; byte-identical |
| 35ca:51a8 | ANDNOT_MASK | 18 | MATCH | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `*p &= ~mask;` (`F7 D0` not ax, then `26 21 07`); byte-identical |
| 2603:c476 | count_up | 18 | RELOCS | src=src/calib/cunit6.c; flags="/G1 /AM /Gs /Os"; `if (g_1cf0 > 0) g_1cf2++;` — 32-bit increment as `83 06 .. 01` + `83 16 .. 00` |
| 1000:1364 | abs_branch | 13 | PENDING | `int __far f(int v) { return (v < 0) ? -v : v; }` reproduces the body exactly (`99` cwd / `33 C2` / `2B C2`) but the epilogue differs: original `5D CB` (pop bp; retf), MSC 7 emits `C9 CB` (leave; retf) at /Os, /Ot, /Ox /Oa /Os and /Oy /Os. Epilogue style is a compiler-generation fingerprint - see CONVENTIONS.md |
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
| 11d8:000c | SET4 | 60 | PENDING | `struct S4 __far *__far f(int a,int b,int c,int d)` storing three words plus `d & 0x7FFF` into a 4-int struct and returning a far pointer to it. **58 of 60 bytes are identical** - only the epilogue differs: original `8B E5 5D CB` (mov sp,bp / pop bp / retf), MSC 7 emits `C9 CB` (leave / retf) under /Os, /Ot, /Od and /Ox. This is the single cleanest instance of the second-generation epilogue: the body is byte-exact, only the frame teardown is not |
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
