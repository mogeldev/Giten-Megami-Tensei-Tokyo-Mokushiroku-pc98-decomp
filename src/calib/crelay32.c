/* Round-19 harvest: two multi-call wrappers with a register parameter.
 * In both, the parameter is a `register` variable (kept in SI) - that is what
 * turns `push word ptr [bp+6]` into `mov si,[bp+6]` + repeated `push si`. */
extern int g_1bba;
extern int __far __pascal fc0(void);
extern int __far __pascal fc2(int a, int b);
extern int __far __pascal fc3(int a);
extern int __far __pascal h1(int a);
extern int __far __pascal h1b(int a, int b);
extern int __far __pascal h5(int a, int b, int c);
extern int __far __pascal h2(int a, int b);
extern int __far __pascal h3(int a);
extern int __far __pascal h4(int a, int b);

int __far __pascal F_3E4F(int a, int b, int c)
{
    register int t;
    fc0();
    t = h1(1);
    h5(a, b, g_1bba);
    h3(t);
    return fc2(c, 0);
}

int __far __pascal F_31F6_0C(register int a)
{
    fc3(h1b(a, a));
    h2(a, 2);
    h1(a);
    h4(a, 3);
    fc0();
    return fc3(0);
}
