/* Round-133 harvest: the largest row in the project so far (138 B).
 *
 * Three details were needed:
 *   - the parameter addresses are cast to `int __far *` - that cast is what makes MSC
 *     emit `lea ax,[bp+0A]` / `push ss` / `push ax` instead of a near `push ax`;
 *   - the guard is `h4(b, c) == 1`, which compiles to `dec ax` / `jnz`;
 *   - it needs `/Ox`, not `/Os`: under `/Os` MSC takes a fresh CX for the second
 *     pointer of `h2`'s argument list instead of reusing AX, which was the last
 *     two-byte difference. */
extern void __far __pascal h1(int __far *a, int __far *b);
extern void __far __pascal h2(int __far *b, int __far *c);
extern void __far __pascal h3(int __far *a, int __far *b);
extern int __far __pascal h4(int a, int b);
extern int __far __pascal h5(int x, int y, int z);
extern void __far __pascal h6(void);

int __far __pascal f(int a, int b, int c)
{
    register int r;

    h1((int __far *)&a, (int __far *)&b);
    h2((int __far *)&b, (int __far *)&c);
    h3((int __far *)&a, (int __far *)&b);
    if (h4(b, c) == 1) {
        r = h5(b, c, 0);
        if (r >= 0x20) r = h5(0, a, 1);
    } else {
        r = h5(b, c, 1);
        if (r >= 0x20) r = h5(0, a, 0);
    }
    h6();
    return r;
}
