/* Round-13 harvest: the six siblings at 36e7 all share one shape - four
 * parameters relayed, then a DGROUP far pointer (`1E 68 <disp>`), the third
 * parameter and a constant, then the third parameter returned. */
extern char g_21c6[];
extern int __far __pascal fc4(int a, int b, int c, int d);
extern int __far __pascal fc3(char __far *p, int a, int b);

int __far __pascal F_36E7(int a, int b, int c, int d)
{
    fc4(a, b, c, d);
    fc3(g_21c6, c, 1);
    return c;
}
