/* Argument arithmetic on a relay call, original 3d1a:0008 (23 B, RELOCS, far pascal retf 6).

     8B 46 0A        first declared argument (at bp+0x0A)
     80 C4 02        add ah,2                     <- adds 0x200 to the value
     50              push it (first argument of the callee)
     FF 76 08        second argument
     FF 76 06        third argument
     E8 <rel>        call
     C9 CA 06 00     leave; retf 6

   `80 C4 02` is `add ah,2`, i.e. `+ 0x200` on a 16-bit value - the tell that the
   constant is applied to the high byte. */
extern void __near __pascal HELP3(int, int, int);

void __far __pascal add_200(int a, int b, int c)
{
    HELP3(a + 0x200, b, c);
}