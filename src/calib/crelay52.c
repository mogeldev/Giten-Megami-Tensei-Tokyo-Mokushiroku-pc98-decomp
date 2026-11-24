/* Round-46 harvest: a running sum through three call pairs, then a signed divide
 * by three and a constant offset, returning a zero-extended byte.
 * The divide and the offset must be **separate statements**: the combined
 * expression makes MSC load AX before CX and fold the `+ 5` into the accumulator,
 * while the split form matches the original (CX=3 first, then AX=SI, then
 * `si += 5`). */
extern int __far __pascal nc(int a);
extern int __far __pascal g1(int a);
extern int __far __pascal h1(int a);

int __far __pascal F_5155(int a, int b, int c)
{
    register int t;
    t = g1(nc(a));
    t += g1(nc(b));
    t += g1(nc(c));
    t = t / 3;
    t = t + 5;
    return (unsigned char)h1(t);
}
