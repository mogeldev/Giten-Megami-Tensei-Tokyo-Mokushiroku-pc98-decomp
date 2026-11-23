/* Round-5 harvest, /Os group. */
extern int g_1bba;
extern int __far __pascal sub0(void);
extern int __far __pascal sub1(int a);
extern int __far __pascal sub4(int a, int b, int c, int d);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a, int b);

int __far __pascal F_31F6_9C(int a) { return h1(sub1(a)); }

int __far F_3E44(void)
{
    if (g_1bba != -1) {
        sub1(g_1bba);
        g_1bba = -1;
    }
    return g_1bba;
}

int __far __pascal F_3E19(int a, int b)
{
    sub4(3, 0, 0, -1);
    return h2(a, b);
}
