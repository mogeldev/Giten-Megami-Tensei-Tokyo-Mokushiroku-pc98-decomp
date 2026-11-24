/* Round-20 harvest: a four-parameter guarded relay and its sibling. Both take a
 * `register` third parameter, call a four-argument relay, call again with a
 * DGROUP far pointer plus that parameter, and only then branch on the first
 * result. The sibling's second branch passes its constant in AX because that
 * callee is `__fastcall` (`B8 24 00` with no push). */
extern char g_17d2[];
extern int __far __pascal fc4(int a, int b, int c, int d);
extern int __far __pascal fc4b(char __far *p, int a, int b);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(void);
extern int __far __fastcall h3(int a);

int __far __pascal F_3B72(int a, int b, register int c, int d)
{
    register int r;
    r = fc4(a, b, c, d);
    fc4b(g_17d2, c, 1);
    if (r) {
        h1(1);
        h2();
    }
    return c;
}

int __far __pascal F_3B6E(int a, int b, register int c, int d)
{
    register int r;
    r = fc4(a, b, c, d);
    fc4b(g_17d2, c, 1);
    if (r) {
        h1(1);
        h3(0x24);
    }
    return c;
}
