/* Round-171 harvest: a lazy initialisation guarded on a global.
 *
 * The function has no frame at all (it starts with `83 3E`, a direct memory compare), which
 * is what MSC emits for a near cdecl function with no parameters and no locals. Both
 * spellings of the guard (`!g` and `g == 0`) produce identical code. */
extern int __far __pascal h(int a, int b);
extern int g_1934;

void __near __cdecl F_3C09(void)
{
    if (!g_1934) g_1934 = h(0x100, 2);
}
