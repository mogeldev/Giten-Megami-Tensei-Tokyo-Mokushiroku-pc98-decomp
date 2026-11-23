/* 32-bit getter pairs: mov ax,[lo]; mov dx,[hi]; ret  (DX:AX return).
   Originals:
     1871:d0e4 (=257f:0004): DGROUP 0x13D2, FAR   -> long get_l(void)
     35ca:3c34 (=398d:0004): DGROUP 0x14C4, NEAR  -> long __near get_ln(void)
   disp16 operands are DGROUP fixups -> RELOCS. */
long g_long_f;
long g_long_n;

long get_l(void)
{
    return g_long_f;
}

long __near get_ln(void)
{
    return g_long_n;
}
