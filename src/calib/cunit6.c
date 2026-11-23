/* Batch from the 14..30 band (round 48).

   1000:1364 (14 B): 55 8B EC 8B 46 06 99 33 C2 2B C2 5D CB
                     -> cwd / xor ax,dx / sub ax,dx = the sign-fold abs idiom:
                        return (v ^ (v >> 15)) - (v >> 15);
   35ca:5198 (16 B): 55 8B EC 8B 46 06 C4 5E 08 26 09 07 C9 CA 06 00
                     -> *p |= mask   (26 09 07 = or es:[bx],ax, store form)
   35ca:51a8 (18 B): 55 8B EC 8B 46 06 F7 D0 C4 5E 08 26 21 07 C9 CA 06 00
                     -> *p &= ~mask (F7 D0 = not ax)
   2603:c476 (18 B): 83 3E F0 1C 00 7E 0A 83 06 F2 1C 01 83 16 F4 1C 00 CB
                     -> if (g_1cf0 > 0) g_1cf2++;   (add 1 / adc 0 = 32-bit increment)

   Parameter order follows the round-35 rule: pascal pushes left to right, so the
   argument at the lower offset ([bp+6]) is the LAST declared one.
*/
int g_1cf0;
long g_1cf2;

int __far __pascal fold_abs(int v)
{
    return (v ^ (v >> 15)) - (v >> 15);
}

void __far __pascal or_mask(int __far *p, int mask)
{
    *p |= mask;
}

void __far __pascal andnot_mask(int __far *p, int mask)
{
    *p &= ~mask;
}

void __far count_up(void)
{
    if (g_1cf0 > 0)
        g_1cf2++;
}
