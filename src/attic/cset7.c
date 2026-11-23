struct S4 {
    int a, b, c, d;
};

struct S4 g_4a78;

struct S4 __far *__far set4(int a, int b, int c, int d)
{
    g_4a78.a = a;
    g_4a78.b = b;
    g_4a78.c = c;
    g_4a78.d = d & 0x7FFF;
    return &g_4a78;
}
