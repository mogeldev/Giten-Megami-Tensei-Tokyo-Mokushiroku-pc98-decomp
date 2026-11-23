/* Branchless far-pointer span, original 37ad:000c (23 B, MATCH, near pascal retn 6).

     C4 5E 06         les bx,[bp+6]      <- far pointer (first declared argument)
     26 8B 47 04      mov ax,es:[bx+4]   <- p[2]
     26 2B 07         sub ax,es:[bx]     <- minus p[0]
     C1 E0 03         shl ax,3
     03 46 04         add ax,[bp+4]      <- plus the last declared argument
     C9 C2 06 00      leave; retn 6

   Near pascal with a far pointer: the pointer occupies bp+6..9 and the int sits
   at bp+4. No branches, so the padding/block-order traits cannot interfere. */
int __near __pascal span8(int __far *p, int a)
{
    return ((p[2] - p[0]) << 3) + a;
}