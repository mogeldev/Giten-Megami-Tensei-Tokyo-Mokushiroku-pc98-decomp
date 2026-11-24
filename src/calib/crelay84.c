/* Round-166 harvest: a `void` function that looks like it returns 0.
 *
 * The original's skip path falls straight into the epilogue without zeroing AX, so the
 * source has no `return 0` at all - it is a `void` function whose caller happens to see the
 * zero left over from the `or ax,ax` test. Writing `int f(...) { if (...) return h2(a);
 * return 0; }` adds a `33 C0` that the image does not have.
 *
 * The byte arguments push as-is because both callees declare their first parameter `char`
 * (see docs/CONVENTIONS.md). */
extern int __far __pascal h1(char a, int b);
extern int __far __pascal h2(char a);

void __far __pascal F_2127(char a, int b)
{
    if (h1(a, b)) h2(a);
}
