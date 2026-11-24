/* Round-240 harvest: a 32-bit running maximum, and a third instance of the near/far tell.
 *
 * Round 222 transcribed this and could not reconcile the parameter offsets; round 238's rule
 * explains them. The epilogue is `ret 8` and the first parameter is read at `[bp+04]`, so the
 * function is **`__near __pascal`**. With `__far` every offset is two bytes higher, which is
 * exactly what made the subtraction look like it was using the wrong operands.
 *
 * The body is a signed 32-bit comparison done the long way round: load the old maximum into
 * DX:AX, subtract with a borrow chain into the accumulator, then compare the high words
 * (signed `jl`/`jg`) before the low word (unsigned `jbe`). */
extern long g_40ac, g_40b0;

void __near __pascal F_1E2F(long a, long b)
{
    long v;

    v = g_40b0;
    g_40ac += b - a;
    if (g_40ac > v) g_40b0 = g_40ac;
}
