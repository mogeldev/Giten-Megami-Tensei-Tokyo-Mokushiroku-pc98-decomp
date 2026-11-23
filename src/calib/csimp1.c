int abs(int);

int g_9b3e;
int g_98fc;

void __far __pascal flag_pair(char __far *a, char __far *b)
{
    g_9b3e = 0;
    g_98fc = 0;
    a[0x186] |= 0x80;
    a[0x185] |= 0x80;
    b[0x185] |= 0x80;
}

int __near __pascal weight2(int a, int b, int c)
{
    return 2 * (5 * (abs(a) + 1) + abs(b)) + c;
}