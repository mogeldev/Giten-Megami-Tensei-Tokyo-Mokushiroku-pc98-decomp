/* Round-112 harvest: a two-register guard. The original keeps the parameter in SI and
 * a copy of the global in DI, which needs both to be `register`; the call then pushes
 * DI twice and the store writes SI back. The function has no frame at all. */
extern int g_1cf0;
extern int __far __pascal h(int a, int b);

int __far __pascal f(register int v)
{
    register int old;

    old = g_1cf0;
    if (v == 1 && old == 0) h(old, old);
    g_1cf0 = v;
    return old;
}
