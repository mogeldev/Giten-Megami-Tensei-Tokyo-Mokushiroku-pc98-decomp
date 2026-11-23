int g_40b8;
int g_40ba;
int g_40bc;
int g_40be;

int __far __pascal record_cfg(int a, int b, int c)
{
    register int old;

    old = g_40ba;
    g_40b8 = a;
    g_40ba = b;
    if (c)
        g_40bc = (c == -1) ? 7 : c;
    g_40be = 1;
    return old;
}
