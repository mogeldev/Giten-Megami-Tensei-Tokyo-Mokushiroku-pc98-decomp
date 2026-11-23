/* Round-12 harvest: 32-bit long helpers around a call. `g_1be8 += g_1bec`
 * compiles to `A1 <lo> 8B 16 <hi> 01 06 <lo> 11 16 <hi>` (add/adc) on 8086;
 * the sibling units use sub/sbb and and/and. */
extern long g_1be8, g_1bec;
extern int __far __pascal fc0(void);
extern int __far __pascal fc1(int a);

void __far __pascal F_2D9B_58(int a) { fc1(a); g_1be8 += g_1bec; fc0(); }
void __far __pascal F_2D9B_7C(int a) { fc1(a); g_1be8 -= g_1bec; fc0(); }
void __far __pascal F_2D9B_A0(int a) { fc1(a); g_1be8 &= g_1bec; fc0(); }
