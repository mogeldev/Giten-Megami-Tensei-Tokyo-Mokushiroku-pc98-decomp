/* Round-51 harvest: a guarded four-argument relay that always ends with the
 * DGROUP pointer call and returns the third parameter. */
extern char g_17d2[];
extern int __far __pascal h4(int a, int b, int c, int d);
extern int __far __pascal h4b(char __far *p, int a, int b);
extern int __far __pascal f1(int a);
extern int __far __pascal f2(void);

int __far __pascal F_3B72_40(int a, int b, int c, int d)
{
    if (h4(a, b, c, d)) {
        f1(1);
        f2();
    }
    h4b(g_17d2, c, 1);
    return c;
}
