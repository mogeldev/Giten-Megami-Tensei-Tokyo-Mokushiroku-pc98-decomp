/* Medium single-statement forms mined in round 33.

   2603:3efc (13 B): 55 8B EC 8B 46 06 2B 46 0A C9 CA 08 00
                     -> retf 8 = 4 word args; pascal pushes left to right, so
                        bp+6 is the LAST declared argument and bp+0xA the second:
                        return d - b;
   458e:8306 (10 B): B8 01 00 8A 0E 58 99 D3 E0 C3
                     -> near function: return 1 << g_b9958 (the shift count is
                        the raw byte; "& 0x1f" in the decompiler is its invention)

   Rejected after comparison (kept for the record):
     35ca:8072  ours uses CX as temp, original DX  (8B 0E vs 8B 16) - 1 byte diff
     458e:a4c6  ours has no frame at all, original saves si/di and uses leave
*/
int g_3efc_o;
unsigned char g_b9958;

int __far __pascal f_3efc(int a, int b, int c, int d)
{
    return d - b;
}

int __near f_8306(void)
{
    return 1 << g_b9958;
}
