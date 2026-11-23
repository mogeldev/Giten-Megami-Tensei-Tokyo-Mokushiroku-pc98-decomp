unsigned g_7bc4;

void __near __pascal clear_at(char __far *p, int i)
{
    p[i + 5] = 0;
}

void __far __pascal mix_long(long v)
{
    g_7bc4 &= 0x3FC0;
    g_7bc4 |= (v >> 16) & 0xC03F;
}