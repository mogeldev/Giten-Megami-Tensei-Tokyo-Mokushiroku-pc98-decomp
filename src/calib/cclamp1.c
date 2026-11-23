/* Zwei Clamp-Geschwister (Runde 23), Originale:
     1f2d:000e (20 B): cmp ax,1 / jge +4 / mov ax,1 / ret
                       mov dx,[0x4688] / cmp ax,dx / jle +2 / mov ax,dx / ret
     1f2f:0002 (20 B): identische Form, Global 0x468A
   Variante: verschachtelter Ternaer, damit MSC den Globalwert in DX haelt. */
int g_4688;
int g_468a;

int __near __fastcall clamp_a(int x)
{
    return (x < 1) ? 1 : ((x > g_4688) ? g_4688 : x);
}

int __near __fastcall clamp_b(int x)
{
    return (x < 1) ? 1 : ((x > g_468a) ? g_468a : x);
}
