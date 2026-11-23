/* conv — Original 458e:a1f6 (16 B, __near __pascal, 1 int-Param):
     55 8b ec          push bp; mov bp,sp
     8b 5e 04          mov bx,[bp+4]
     03 db             add bx,bx              (Index *2)
     8b 87 6a 39       mov ax,[bx+0x396A]     (Wort-Lookup, disp16=Fixup)
     c9 c2 02 00       leave; retn 2          (Near-Pascal: Callee raeumt ab)
   Semantik: Uebersetzungstabelle (Byte -> Wort), Basis DGROUP 0x396A. */
char conv_table[512];

int __near __pascal conv(int c)
{
    return *(int __near *)&conv_table[c + c];
}
