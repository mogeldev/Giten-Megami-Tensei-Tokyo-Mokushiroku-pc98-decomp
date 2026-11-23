unsigned char g_8670[0x400];

unsigned __far __pascal getbyte_u(int i)
{
    return g_8670[i * 4];
}

unsigned __far __pascal and3u(unsigned a, unsigned b)
{
    return (a + b) & 3;
}