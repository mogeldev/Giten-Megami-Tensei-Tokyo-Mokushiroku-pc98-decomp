/* Canonical far-pascal one-parameter forms found at real code boundaries
   (round 28). Inventory sizes for these addresses are inflated because Ghidra
   merged several units into one function; the real lengths come from the
   `C9 CA 02 00` terminator sequence.

     2f22:0006 (13 B): A3 1C48            -> g_1c48 = v;
     1fc8:0000 (16 B): 09 06 F6 00 / A1 F6 00 -> g_00f6 |= v; return g_00f6;
     1fc8:0010 (18 B): F7 D0 / 21 06 F6 00 / A1 F6 00 -> g_00f6 &= ~v; return g_00f6;

   disp16 operands are DGROUP relocations -> RELOCS. */
int g_1c48;
int g_00f6;

void __far __pascal set_1c48(int v)
{
    g_1c48 = v;
}

int __far __pascal or_ret_f6(int v)
{
    g_00f6 |= v;
    return g_00f6;
}

int __far __pascal andnot_ret_f6(int v)
{
    g_00f6 &= ~v;
    return g_00f6;
}
