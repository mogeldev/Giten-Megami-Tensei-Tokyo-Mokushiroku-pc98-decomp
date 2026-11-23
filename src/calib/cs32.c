/* Large relay call, original 23d7:0000 (41 B, RELOCS, far pascal retf 12).

     FF 76 10 .. FF 76 08     push the six arguments in order (first declared at bp+0x10)
     6A 00 6A 00 6A 00 6A 00  four zero constants
     6A 4F / 68 8F 01        constants 0x4F and 0x18F (the latter needs a 16-bit push)
     FF 76 06                the last declared argument
     E8 <rel>                call
     C9 CA 0C 00             leave; retf 12

   `retf 12` fixes the argument count at six words; the constants are literals in
   the middle of the list, which is why the push count (12) exceeds the argument
   count (6). */
extern void __near __pascal HELP12(int, int, int, int, int, int, int, int, int, int, int, int);

void __far __pascal big_call(int a, int b, int c, int d, int e, int f)
{
    HELP12(a, b, c, d, e, 0, 0, 0, 0, 0x4F, 0x18F, f);
}