char __far *__far __pascal put_be(char __far *p, int a, int b)
{
    *p = (char)((a + b) >> 8);
    p[1] = (char)(a + b);
    p[2] = 0;
    p += 2;
    return p;
}
