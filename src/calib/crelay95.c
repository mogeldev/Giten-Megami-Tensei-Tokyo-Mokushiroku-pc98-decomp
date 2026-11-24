/* Round-238 harvest: rotating a `long` array right by one element.
 *
 * The tell that made this one work: the epilogue is `ret 2` (near) and the parameter is read at
 * `[bp+04]`, so the function is **`__near __pascal`** - a far function would have its parameters
 * starting at `[bp+06]` (return IP at `+02`, return CS at `+04`). Reading a parameter at `+04`
 * in a function whose epilogue is a plain `ret n` is the signature of near pascal. */
extern long g_866e[];

void __near __pascal F_4332(int n)
{
    long t;

    t = g_866e[n];
    while (n > 0) { g_866e[n] = g_866e[n - 1]; n--; }
    g_866e[0] = t;
}
