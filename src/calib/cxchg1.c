int g_1cea;
int g_1d52;
int g_2a28;
int g_417c;

int __far __pascal xchg_1cea(int v)
{
    int old = g_1cea;

    g_1cea = v;
    return old;
}

int __far __pascal xchg_1d52(int v)
{
    int old = g_1d52;

    g_1d52 = v;
    return old;
}

int __far __pascal xchg_2a28(int v)
{
    int old = g_2a28;

    g_2a28 = v;
    return old;
}

int __far __pascal xchg_417c(int v)
{
    int old = g_417c;

    g_417c = v;
    return old;
}