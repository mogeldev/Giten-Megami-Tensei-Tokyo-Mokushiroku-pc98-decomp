/* Exchange with follow-up resets, original 35ca:8012 (22 B, frameless, retf):
     8B 16 C6 78   mov dx,[0x78C6]     <- old value into DX ( /Ox allocation )
     A3 C6 78      mov [0x78C6],ax     <- store the incoming AX
     33 C0         xor ax,ax
     A3 C8 78      mov [0x78C8],0
     A3 CA 78      mov [0x78CA],0
     A3 CC 78      mov [0x78CC],0
     8B C2         mov ax,dx           <- return old
     CB            retf
   Same shape as 35ca:8072 (round 33), therefore the same per-file flags: /Ox. */
int g_78c6;
int g_78c8;
int g_78ca;
int g_78cc;

int __fastcall swap_reset(int v)
{
    int old;

    old = g_78c6;
    g_78c6 = v;
    g_78c8 = 0;
    g_78ca = 0;
    g_78cc = 0;
    return old;
}
