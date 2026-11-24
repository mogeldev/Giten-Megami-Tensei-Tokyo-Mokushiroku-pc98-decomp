/* Round-114 harvest: a long-result guard. The original passes the far-pointer constant
 * as two plain int arguments (`0x0871`, `0x760E` pushed as words), so `MK_FP` must not
 * be used - it makes MSC call a helper - and the comparison is against `-1L`, which is
 * what produces the `cmp ax,-1` / `cmp dx,ax` pair. */
extern long __far __cdecl h(int a, int b, int c);
extern char g_0128[];
extern int __far __cdecl h2(int a, char __far *p);

void __far __pascal f(int a)
{
    if (h(a, 0x760E, 0x0871) == -1L) h2(0x48, g_0128);
}
