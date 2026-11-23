/* Round-4 harvest, /Ox group (SI register staging). */
extern int g_2d0c;
extern int __far __pascal sub0(void);
extern int __far __pascal sub1(int a);
extern int __far __pascal h2(int a, int b);

int __far __pascal F_4E9A(int a)
{
    int t;
    t = sub0();
    g_2d0c = a;
    return t;
}

int __far __pascal F_31F3(register int a)
{
    sub1(a);
    return h2(a, 2);
}
