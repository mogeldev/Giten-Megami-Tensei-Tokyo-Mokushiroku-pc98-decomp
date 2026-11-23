#define MK_FP(seg, off) ((char __far *)(((unsigned long)(seg) << 16) | (unsigned)(off)))

int g_866e[0x400];

char __far *__far __pascal addr4(int i)
{
    return (char __far *)&g_866e[i * 2];
}

int __far __pascal sext11(int i)
{
    return (g_866e[i * 2] << 5) >> 5;
}

char __far *__far __pascal rec6(int i)
{
    return MK_FP(0x4363, i * 0x1E + 6);
}