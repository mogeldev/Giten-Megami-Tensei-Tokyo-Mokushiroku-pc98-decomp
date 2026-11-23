struct E {
    char b[4];
};

struct E g_866e[0x40];

struct E __far *__near __pascal at(int i)
{
    if (i < 0 || i >= 0x40) {
        __asm nop
        return 0;
    }
    return &g_866e[i];
}