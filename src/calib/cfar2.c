/* Far-pointer arithmetic, original 37b0:000a (20 B, MATCH):
     C4 5E 08      les bx,[bp+8]      <- far pointer (first declared argument)
     26 8B 07      mov ax,es:[bx]     <- p[0]
     26 2B 47 04   sub ax,es:[bx+4]   <- p[2]
     03 46 06      add ax,[bp+6]      <- plus the last declared argument
     C9 CA 06 00   leave; retf 6
   -> return (*p - p[2]) + a; */
int __far __pascal sub_p2_add(int __far *p, int a)
{
    return (*p - p[2]) + a;
}
