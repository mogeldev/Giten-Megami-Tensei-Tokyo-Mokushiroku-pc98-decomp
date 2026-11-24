/* Round-43 harvest: a guarded four-argument relay. The third parameter must be
 * `register` (pushed from SI twice) and the first call's result kept in DI; the
 * branch then runs a no-argument call, a one-argument call, and a call whose long
 * result is forwarded. */
extern char g_17d2[];
extern char g_98e4[];
extern int __far __pascal h4(int a, int b, int c, int d);
extern int __far __pascal h4b(char __far *p, int a, int b);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(void);
extern long __far __pascal h3(char __far *p);
extern int __far __pascal h4c(long v);

int __far __pascal F_3BA3(int a, int b, register int c, int d)
{
    register int r;
    r = h4(a, b, c, d);
    h4b(g_17d2, c, 1);
    if (r) {
        h1(1);
        h2();
        h4c(h3(g_98e4));
    }
    return c;
}
