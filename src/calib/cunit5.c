/* Hidden units with arithmetic (round 47).

   20b4:014c (19 B):
     B8 64 00        mov ax,100
     F7 26 3E 0F     mul word [0x0F3E]      <- unsigned 16x16 -> DX:AX
     8A 0E 3D 0F     mov cl,[0x0F3D]
     2A ED           sub ch,ch
     03 C1           add ax,cx
     83 D2 00        adc dx,0
     CB              retf
   -> long r = 100UL * g_word_f3e + g_byte_f3d;

   1466:0052 (9 B):
     55 8B EC        push bp; mov bp,sp
     33 C0           xor ax,ax
     8B E5           mov sp,bp
     5D CB           pop bp; retf
   -> a frame is present although nothing uses it; try the plain `return 0;`
      in several conventions to see which one keeps the frame.
*/
unsigned g_f3e;
unsigned char g_f3d;

unsigned long __far calc_f3e(void)
{
    return (unsigned long)100 * g_f3e + g_f3d;
}

int __far zero_far(void)
{
    return 0;
}

int __far __pascal zero_pascal(void)
{
    return 0;
}
