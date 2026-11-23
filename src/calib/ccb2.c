extern int (__far __pascal *g_cb)(int, int, int, int);

int __near __pascal call4(int a, int b, int c, int d)
{
    if (g_cb)
        a = g_cb(c, d, b, a);
    return a;
}
