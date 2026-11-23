int g_78ca;
int g_78cc;

int __far __fastcall exch_zero(int v)
{
    int old;

    old = g_78ca;
    g_78ca = v;
    g_78cc = 0;
    return old;
}
