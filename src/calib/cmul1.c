/* Unsigned multiply feeding a call, original 21f4:0000 (23 B, RELOCS).

     FF 76 0A / FF 76 08      push a; push b
     8B 46 04 / F7 66 06      ax = [bp+4]; mul word [bp+6]   <- 66 = MUL (unsigned)
     50                       push ax                       <- low word of the product
     E8 <rel>                 call HELP
     C9 C2 08 00              leave; retn 8

   `F7 66` is the unsigned MUL; declaring the operands as `int` makes MSC emit
   `F7 6E` (IMUL) instead, which is the only difference. */
extern int __near __pascal HELP(int, int, unsigned);

int __near __pascal mul_then_call(int a, int b, unsigned c, unsigned d)
{
    return HELP(a, b, d * c);
}