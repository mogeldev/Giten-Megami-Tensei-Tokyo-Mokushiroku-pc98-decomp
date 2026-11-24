/* Round-49 harvest: two straight-line relays.
 * F_3BFC ends with a `__fastcall` tail: `8B C6` loads the argument into AX right
 * before the call, which is what identifies the callee as fastcall (without the
 * prototype MSC would push the value instead).
 * F_2A43 sums two long parameters and forwards the result as the first argument. */
extern int __far __pascal h1(void);
extern int __far __fastcall h2(int a);
extern int __far __pascal h4(int a, int b, int c, int d);

int __far __pascal F_3BFC(int a, int b)
{
    register int r;
    r = h1();
    h4(a, b, 0, 0);
    return h2(r);
}

extern int __far __pascal h6(long v, int a, int b, int c, int d);

void __far __pascal F_2A43(long a, long b, int c, int d, int e, int g)
{
    h6(a + b, c, d, e, g);
}
