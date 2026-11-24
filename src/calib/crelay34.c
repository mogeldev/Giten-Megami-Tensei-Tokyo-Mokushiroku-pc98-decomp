/* Round-21 harvest: a six-iteration loop with two register variables (DI counts,
 * SI is the loop index) and a five-argument chain around one global. */
extern int g_78c4;
extern int __far __pascal fc0(void);
extern int __far __pascal fc2(int a, int b);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a, int b, int c);
extern int __far __pascal h5(int a, int b, int c, int d, int e);

int __far __pascal F_416B(int flags)
{
    register int i;
    register int d;
    d = fc0();
    for (i = 0; i < 6; i++) {
        if (h1(i) >= 0 && (flags & 0x20)) {
            fc2(-1 - i, 0);
            d++;
        }
    }
    return d;
}

void __near __pascal F_3D94(int a, int b)
{
    h1(g_78c4);
    h2(g_78c4, 0, 0);
    h5(g_78c4, a, b, 0x400, 1);
    h1(g_78c4);
}
