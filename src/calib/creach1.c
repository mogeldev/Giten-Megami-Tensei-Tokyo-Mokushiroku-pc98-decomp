int g_1cd0;
int g_1cd2;
int g_4db6;
int g_4db8;

int __near __pascal neg1(int v)
{
    return -1 - v;
}

long __far __pascal pack2(int a, int b)
{
    return ((long)b << 16) | (unsigned)a;
}

void __far __pascal store_at1(char __far *p, int v)
{
    *(int __far *)(p + 1) = v;
}

void __near __pascal store2(int a, int b)
{
    g_1cd0 = a;
    g_1cd2 = b;
}

void __far clear_pair(int v)
{
    g_4db6 = v;
    g_4db8 = 0;
}