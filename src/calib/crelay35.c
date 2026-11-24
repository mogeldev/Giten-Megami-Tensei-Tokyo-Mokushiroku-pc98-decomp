/* Round-22 harvest: a counter-guard unit in a near-Pascal function.
 * Pascal arguments are pushed left to right, so the literal order in the source
 * is exactly the byte order of the pushes (`6A 01 6A 64 6A 02` = (1, 0x64, 2)). */
extern int g_395e;
extern int __far __pascal p3(int a, int b, int c);
extern int __far __pascal fc(int a);

int __near __pascal F_505F(int n)
{
    register int t;
    t = n + g_395e;
    if (p3(1, 0x64, 2) > t) {
        g_395e++;
        if (fc(4) != -1) g_395e++;
        return 0;
    }
    g_395e = 0;
    return 1;
}
