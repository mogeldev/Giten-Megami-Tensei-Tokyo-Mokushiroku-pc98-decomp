/* Round-34 harvest: a long relay into a long-accepting callee, and a multiply
 * where the factors come from a register parameter and the last parameter. */
extern long __far __pascal h4l(int a, int b, int c, int d);
extern int __far __pascal h1l(long v);

void __far __pascal F_2A0F(int a, int b, int c, int d)
{
    h1l(h4l(a, b, c, d));
}

extern int __far __pascal h3i(int a, int b, int c);
extern int __far __pascal h1i(int a);

int __far __pascal F_3891(register int a, int b, int c)
{
    return h1i(h3i(a, b, a) * c);
}
