/* Global exchange, original 35ca:8072 (10 B):
     8B 16 CC 78   mov dx,[0x78CC]      <- old value into DX
     A3 CC 78      mov [0x78CC],ax      <- store incoming AX
     8B C2         mov ax,dx            <- return it
     CB            retf
   Frameless, no stack arguments -> __fastcall (value arrives in AX).

   Per-file flags: this is the first function proven to need /Ox. Under /Os and
   /Ot the allocator picks CX as the temporary (8B 0E .. 8B C1), under /Ox it
   picks DX, which is what the original does. See docs/IDIOMS.md, round 33. */
int g_78cc;

int __fastcall swap_78cc(int v)
{
    int old;

    old = g_78cc;
    g_78cc = v;
    return old;
}
