int g_6e36[0x2000];

void __far __pascal clear_flag(int i, int v)
{
    register int idx;
    int mask;

    idx = i;
    mask = ~v;
    if (idx == -1)
        return;
    g_6e36[idx * 26] &= mask;
}