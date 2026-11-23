/* Round-12 harvest, /Ox group: two-call wrappers whose intermediate value is
 * kept in SI/DI (`register` parameter), so the frame stays a plain push-bp. */
extern int __far __pascal fc0(void);
extern int __far __pascal fc1(int a);
extern int __far __pascal fc2(int a, int b);

void __far __pascal F_31F3_00(register int a)
{
    int t;
    t = fc2(a, a);
    fc1(t);
    fc2(a, 0);
}

int __far __pascal F_4A41_00(register int a, int b)
{
    int r;
    r = fc1(a);
    fc2(a, b);
    return r;
}
