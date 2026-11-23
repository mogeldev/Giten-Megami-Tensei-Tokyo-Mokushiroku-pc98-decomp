/* Far-pointer selector, original 1f6f:000c (44 B, RELOCS, far pascal retf 2).

     8B 5E 06 / 0B DB / 75 09      if (kind == 0)
     A1 <a> / 8B 16 <a+2>          return g_a          (offset/segment loaded separately)
     83 FB 02 / 75 09              if (kind == 2)
     A1 <b> / 8B 16 <b+2>          return g_b
     A1 <c> / 8B 16 <c+2>          return g_c

   The globals sit at 0x46EC (a), 0x46F0 (c) and 0x46F4 (b), so they must be
   declared in that order. /Ox is required: under /Os the parameter is compared in
   memory (`83 7E 06 00`) instead of being staged in BX. */
char __far *g_a;
char __far *g_c;
char __far *g_b;

char __far *__far __pascal pick_ptr(int kind)
{
    if (kind == 0)
        return g_a;
    if (kind == 2)
        return g_b;
    return g_c;
}