/* Round-16 harvest: a five-call long chain and a guarded double call. Two rules
 * both matter here: the discarded result of `h4` must be its own statement (a
 * single nested expression keeps it), and the wrapper returns `int` - declaring
 * it `long` inserts a `cwd` before `leave`. */
extern long __far __pascal c1(int a);
extern long __far __pascal c2(long v, long w);
extern long __far __pascal h3(long v);
extern long __far __pascal h4(long v);
extern int __far __pascal h5(int a);

int __far __pascal F_33C1(int a)
{
    h4(h3(c2(c1(-1), a)));
    return h5(1);
}

extern int g_234c, g_234e;
extern int __far __pascal fc0(void);
extern int __far __pascal fc2(int a, int b);

void __far __pascal F_48AA(int a)
{
    if (!g_234c) {
        if (a || g_234e) {
            fc0();
            fc2(0, 1);
        }
        g_234e = 0;
    }
}
