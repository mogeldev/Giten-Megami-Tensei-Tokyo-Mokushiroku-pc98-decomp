/* Round-133 harvest, second row: the register-reuse wall falls to `/Ox`.
 *
 * Under `/Os` MSC gave the two register parameters to SI and DI in an order that swaps
 * them against the original (round 116 recorded it as four contradictory data points).
 * Under `/Ox` the allocation matches exactly, so this unit and its byte-identical
 * sibling `2191:0008` both verify. */
extern int __near __pascal h1(int a);
extern long __far __pascal h2(int a, int b);
extern int __near __pascal h3(long r, int a, int b);

void __far __pascal F_218F(register int a, register int b)
{
    h1(-1);
    h3(h2(a, b), a, b);
}
