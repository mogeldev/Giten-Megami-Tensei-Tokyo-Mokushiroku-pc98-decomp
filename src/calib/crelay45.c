/* Round-37 harvest: two straight-line relays.
 * F_2F3F: a long global is pushed as a far argument and the result stored back.
 * F_3E4F: six calls in a row, two of them `__fastcall` (argument in AX, no push). */
extern long g_1c36;
extern int g_1c48;
extern long __far __pascal h5(long v, int a, int b, int c);

int __far __pascal F_2F3F(int x)
{
    g_1c36 = h5(g_1c36, x, 0, g_1c48);
    return 0;
}

extern int g_1bba;
extern int __far __fastcall f1(int a);
extern int __far __fastcall f2(int a);
extern int __far __pascal h3(void);
extern int __far __pascal h4(void);
extern int __far __pascal h5b(int a);
extern int __far __pascal h6(int a, int b, int c);

void __far __pascal F_3E4F(int a, int b, int c)
{
    f1(0x23);
    f2(c);
    h3();
    h4();
    h5b(1);
    h6(a, b, g_1bba);
}
