/* Round-13 harvest: nested chains and a guarded store. */
extern int g_234c, g_234e;
extern int __far __pascal fc0(void);
extern int __far __pascal fc1(int a);
extern int __far __pascal fc3(int a, int b, int c);
extern int __far __pascal fc4(int a, int b, int c, int d);
extern int __far __pascal h(int a);
extern int __near __pascal nn(int a, int b);

/* `1 - h(...)` compiles to `48 F7 D8` (dec / neg) */
int __far __pascal F_2D49_4A(int a) { return fc3(1 - h(fc1(fc0())), a, 0); }

int __far __pascal F_3A3F_8C(register int a, int b, int c, int d)
{
    return nn(fc1(fc4(a, a, b, c)), d);
}

/* the `g_234e = 0` store sits inside the outer guard */
void __far __pascal F_48AD(int a)
{
    if (!g_234c) {
        if (a || g_234e) fc0();
        g_234e = 0;
    }
}
