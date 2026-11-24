/* Round-44 harvest: a chain of four `__fastcall` relays (argument in AX, no push)
 * followed by a guarded three-argument call, and an init unit that stores a long
 * global around two calls. */
extern int __far __fastcall f1(int a);
extern int __far __fastcall f2(int a);
extern int __far __fastcall f3(int a);
extern int __far __fastcall f4(int a);
extern int __far __pascal f5(int a, int b, int c);

void __far __pascal F_3E15(register int a, int b, int c, int d)
{
    f1(1);
    f2(a);
    f3(b);
    f4(c);
    if (d >= 0 && a == 1) f5(d, -1, -1);
}

extern int g_466e;
extern long g_466a;
extern void __far __pascal h1(void);
extern void __far __pascal h2(void);
extern void __far __pascal h3(int a, int b);

void __far __pascal F_1EC4(long v)
{
    if (g_466e) h1();
    g_466a = v;
    h2();
    h3(0x0871, 0x6614);
    g_466e = 1;
}
