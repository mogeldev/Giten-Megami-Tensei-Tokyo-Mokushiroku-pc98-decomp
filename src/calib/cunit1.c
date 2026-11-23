/* Functions recovered from the split inventory (round 41) - units that the
   decompiler had merged into bigger entries, so they were invisible before.

     2e01:0014 (8 B):  A1 C2 7B / 8B 16 C4 7B / CB
                       -> long getter: return the long at 0x7BC2
     4a91:001e (8 B):  same shape for the long at 0x9973
     477b:0028 (10 B): A1 71 99 / C1 E0 02 / C1 F8 02 / CB
                       -> return (g << 2) >> 2, i.e. sign-extend a 14-bit value
     3eec:0058 (13 B): A1 CE 29 / A3 D0 29 / C7 06 C8 29 FF FF / CB
                       -> g_29d0 = g_29ce; g_29c8 = -1;

   Skipped: 159d:190d (stosw against a pointer taken from an absolute address)
   and 1534:02a5 (two thunks, addresses 0x0004/0x00A4 look like interrupt
   vectors) - both read as hand-written assembly.
*/
long g_7bc2;
long g_9973;
int g_9971;
int g_29ce;
int g_29d0;
int g_29c8;

long __far get_long_7bc2(void)
{
    return g_7bc2;
}

long __far get_long_9973(void)
{
    return g_9973;
}

int __far sext14(void)
{
    return (g_9971 << 2) >> 2;
}

void __far copy_and_reset(void)
{
    g_29d0 = g_29ce;
    g_29c8 = -1;
}
