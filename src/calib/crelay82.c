/* Round-162 harvest: a byte returned in AL, shifted into the high half.
 *
 * The original's second half is `8A E0 2A C0` - `mov ah,al` / `sub al,al` - i.e. it takes
 * the low byte of the second call and moves it to the high half of AX. That is exactly
 * what MSC emits for `(unsigned)h2(...) << 8` when `h2` returns `unsigned char`; writing
 * the same operation as `h2(...) >> 8` on an `unsigned` return produces `mov al,ah`
 * instead and is a different program. */
extern unsigned char __far __pascal h1(int a, int b, int c);
extern unsigned char __far __pascal h2(int a, int b, int c);

int __far __pascal F_2B4B(int a0, int b, int c)
{
    register int d, x;

    d = a0;
    x = h1(d, b, c);
    return x + ((unsigned)h2(d, b, c) << 8);
}
