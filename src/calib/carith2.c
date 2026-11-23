/* Round 66 batch 2 - the two that verified.

   47ea:000a (20 B, far pascal retf 2):
     8B 56 06 / 83 FA 63 / 7E 03 / BA 63 00 / 8B C2  -> unsigned clamp to 0x63
     Note `7E` (jle): the comparison is signed against 0x63 here.

   4384:000c (20 B, far pascal retf 2):
     8B 5E 06 / C1 E3 02 / 8A 87 71 86 / 25 7F 00
     -> byte from a stride-4 array at +1, masked to 7 bits.
*/
unsigned char g_8670[0x400];

int __far __pascal clamp63(int v)
{
    if (v > 0x63)
        v = 0x63;
    return v;
}

int __far __pascal maskbyte(int i)
{
    return g_8670[i * 4 + 1] & 0x7F;
}