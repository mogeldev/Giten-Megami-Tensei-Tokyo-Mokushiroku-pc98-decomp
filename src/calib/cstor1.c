int g_13fa;
int g_13fc;
int g_13fe;
int g_1400;
int g_2b0e;
int g_2b10;

void __far __pascal store4(int a, int b, int c, int d)
{
    g_13fa = a;
    g_13fc = b;
    g_13fe = c;
    g_1400 = d;
}

void __far __pascal store_if(int a, int b)
{
    if (a != -1)
        g_2b0e = a;
    if (b != -1)
        g_2b10 = b;
}
