/* Round-244 harvest: three sibling family members at once.
 *
 * `*p = h(*p)` through a far pointer, with a near callee. The function is `__near __pascal`
 * (epilogue `ret 4`, first parameter at `[bp+04]` - round 238's rule), the pointer parameter is
 * `int __far *` so it becomes an offset at `[bp+04]` and a segment at `[bp+06]`, and `h` is
 * **near**: the image's call is `E8`, not the `9A`/`90 0E E8` pair a far call would leave.
 *
 * One source shape matches **three** inventory rows - `3807:0004`, `380c:0000` and `3811:0004`
 * are 28-byte windows whose real function is 26 bytes, differing only in which function they
 * call. The last two bytes of each window are padding, not code. */
extern int __near __pascal h(int v);

void __near __pascal F_3807(int __far *p)
{
    *p = h(*p);
}
