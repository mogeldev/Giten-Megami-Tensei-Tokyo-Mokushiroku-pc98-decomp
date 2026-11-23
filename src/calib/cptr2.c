/* Far-pointer arithmetic accessors, round 35.

   35ca:1e54 (22 B, near pascal, retn 6):
     C4 5E 06 les bx,[bp+6] / 26 8B 47 06 es:[bx+6] / 26 2B 47 02 sub es:[bx+2]
     / 03 46 04 add ax,[bp+4]  ->  (p[3] - p[1]) + a
     Near frame: [bp+4] = first declared argument (int a), [bp+6] = the far pointer.

   35ca:1e7e (22 B, far pascal, retf 6):
     26 8B 47 02 / 26 2B 47 06 / 03 46 06  ->  (p[1] - p[3]) + a
     Far frame: arguments start at [bp+6].

   35ca:5550 (22 B, far pascal, retf 6):
     C4 5E 08 les bx,[bp+8] / 26 8B 07 mov ax,es:[bx] / 23 46 06 and ax,[bp+6]
     / 3D 01 00 cmp ax,1 / 1B C0 sbb ax,ax / 40 inc ax  ->  (*p & mask) != 0
     The load is a WORD, so the pointer is int __far *.

   Skipped: 2603:5306 and 1871:8b0a use `03 F6` / `03 DB` (add si,si / add bx,bx)
   for the index scaling, which neither MSC generation emits (see CONVENTIONS.md).
*/
int __near __pascal sub_p3_p1(int __far *p, int a)
{
    return (p[3] - p[1]) + a;
}

int __far __pascal sub_p1_p3(int __far *p, int a)
{
    return (p[1] - p[3]) + a;
}

int __far __pascal test_and(int __far *p, int mask)
{
    return (*p & mask) != 0;
}
