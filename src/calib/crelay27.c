/* Round-13 harvest: early-out with an implicit return, a six-argument relay and
 * a call whose third argument is a *constant pointer*. */
extern int g_1bec, g_1bee;
extern int __far __pascal fc0(void);
extern int __far __pascal fc1(int a);
extern int __far __pascal fc2(int a, int b);
extern int __far __pascal fc3(int a, int b, int c);
extern int __far __pascal fc4(int a, int b, int c, int d);

/* the `return -1` lives inside the if; the fall-through leaves AX as fc0()'s
 * result, which is exactly what the original does */
int __far __pascal F_1EC4(int a, int b)
{
    if (fc0()) { fc1(1); fc2(a, b); return -1; }
}

int __far __pascal F_3A3F_66(register int a, int b, int c)
{
    return fc1(fc1(fc4(a, a, b, c)));
}

/* `68 E8 1B` is a constant pointer argument, not a symbol load */
int __far __pascal F_2D97_1E(int a)
{
    fc1(a);
    fc3(g_1bee, g_1bec, 0x1BE8);
    fc0();
}
