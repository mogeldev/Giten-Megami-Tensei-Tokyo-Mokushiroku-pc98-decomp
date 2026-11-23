/* 32-bit exchanges, round 37 - two siblings of the same shape.

   1871:5c26 (38 B, far pascal, retf 4 - one long argument):
     C8 04 00 00   enter 4                     (one long of locals)
     A1 C0 40      mov ax,[0x40C0]             low word of the global long
     8B 16 C2 40   mov dx,[0x40C2]             high word
     8B D8         mov bx,ax                   keep low in BX
     89 56 FE      mov [bp-2],dx               spill high
     8B 46 06      mov ax,[bp+6]               incoming low
     8B 56 08      mov dx,[bp+8]               incoming high
     A3 C0 40      mov [0x40C0],ax
     89 16 C2 40   mov [0x40C2],dx
     8B C3         mov ax,bx                   return old low ...
     8B 56 FE      mov dx,[bp-2]               ... and old high
     C9 CA 04 00   leave; retf 4
   ->  long f(long v) { long old = g; g = v; return old; }

   35ca:209c (38 B) is the same shape with the long at 0x13F6/0x13F8.
*/
long g_40c0;
long g_13f6;

long __far __pascal swap_long_40c0(long v)
{
    long old;

    old = g_40c0;
    g_40c0 = v;
    return old;
}

long __far __pascal swap_long_13f6(long v)
{
    long old;

    old = g_13f6;
    g_13f6 = v;
    return old;
}
