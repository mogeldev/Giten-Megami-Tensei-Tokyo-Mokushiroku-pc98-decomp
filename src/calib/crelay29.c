/* Round-15 harvest: a long-argument relay and a difference of two call chains.
 * Note that the first callee must *return* long (`52 50` pushes its DX:AX);
 * declaring it int makes MSC insert a `cwd` before the push. */
extern int __far __pascal fc1(int a);
extern long __far __pascal fc4(long a, long b, long c, long d);
extern int __far __pascal fc1l(long v);
extern int __far __pascal h1(int a);

int __far __pascal F_2A45(int a, int b, int c, int d)
{
    return fc1l(fc4(a, b, c, d));
}

int __far __pascal F_50C4(int a, int b)
{
    register int t;
    t = h1(fc1(a));
    return t - h1(fc1(b));
}
