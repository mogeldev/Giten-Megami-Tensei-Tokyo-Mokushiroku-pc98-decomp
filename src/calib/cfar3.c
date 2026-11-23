/* XOR-then-test, original 3b1b:0002 (21 B, MATCH, per-file /Ox /Oa /Os):
     8B 5E 06      mov bx,[bp+6]      <- the mask is staged in BX first
     8B C3         mov ax,bx
     C4 5E 08      les bx,[bp+8]
     26 31 07      xor es:[bx],ax     <- *p ^= mask
     26 23 07      and ax,es:[bx]     <- result in AX, memory NOT stored
     C9 CA 06 00   leave; retf 6
   -> *p ^= mask; return mask & *p;   with the mask copied through a local so
      the allocator keeps it in BX (only /Ox does that; /Os spills a frame). */
int __far __pascal xor_and(int __far *p, int mask)
{
    int m = mask;

    *p ^= m;
    return m & *p;
}
