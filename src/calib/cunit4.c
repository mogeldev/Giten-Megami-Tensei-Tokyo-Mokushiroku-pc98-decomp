/* Fastcall store setters recovered by the widened split rule (round 44).

     1534:02aa (4 B): A3 A4 00 C3   mov [0x00A4],ax ; retn
     25f0:013a (4 B): A3 9E 40 CB   mov [0x409E],ax ; retf

   No prologue, no stack argument, value arrives in AX -> __fastcall. The near
   variant ends with C3, the far one with CB, so the model is read off the
   terminator (docs/IDIOMS.md, round 33).
*/
int g_00a4;
int g_409e;

void __near __fastcall set_near_a4(int v)
{
    g_00a4 = v;
}

void __far __fastcall set_far_409e(int v)
{
    g_409e = v;
}
