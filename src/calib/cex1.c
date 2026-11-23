/* Three functions stored back to back, original 458e:705a (44 B merged blob):
   real units are 19 + 1 gap + 19 + 1 gap + 4 bytes.

     55 8B EC          push bp; mov bp,sp         <- frame, so NOT fastcall
     8B 16 1A 2C       mov dx,[0x2C1A]           <- old value into DX
     8B 46 06          mov ax,[bp+6]             <- one stack argument
     A3 1A 2C          mov [0x2C1A],ax
     8B C2             mov ax,dx
     C9 CA 02 00       leave; retf 2
        -> __far __pascal exchange, temp in DX

     ... same shape for 0x2C24 ...
     A1 24 2C CB       mov ax,[0x2C24]; retf      -> plain getter
*/
int g_2c1a;
int g_2c24;

int __far __pascal swap_2c1a(int v)
{
    int old;

    old = g_2c1a;
    g_2c1a = v;
    return old;
}

int __far __pascal swap_2c24(int v)
{
    int old;

    old = g_2c24;
    g_2c24 = v;
    return old;
}

int __far get_2c24(void)
{
    return g_2c24;
}
