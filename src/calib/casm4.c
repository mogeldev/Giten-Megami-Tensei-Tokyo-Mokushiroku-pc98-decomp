/* `add bx,bx`: Microsoft C 7 always emits `shl bx,1` (trait 1), so the index
   scaling is written in inline assembly. Everything else is compiler output.
   Original 35ca:2306 (16 B):
     55 8B EC / 8B 5E 04 / 03 DB / 8B 87 2A 14 / C9 C2 02 00
   This is an ASM row: byte-verified, but it does not demonstrate C source. */
int g_142a[256];

int __near __pascal idx_142a(int i)
{
    __asm mov bx, i
    __asm add bx, bx
    __asm mov ax, g_142a[bx]
}
