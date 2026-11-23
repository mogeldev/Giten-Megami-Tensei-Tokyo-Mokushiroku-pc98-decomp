int g_142a[256];

int __near __pascal idx(int i)
{
    __asm mov bx, i
    __asm add bx, bx
    __asm mov ax, g_142a[bx]
    return _AX;
}