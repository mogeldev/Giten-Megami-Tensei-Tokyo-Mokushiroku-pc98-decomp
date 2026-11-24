/* Round-109 harvest: a nested call chain whose inventory window cuts it short.
 * `units.csv` says 28 bytes for this one; the function is 34 - the window ends inside
 * the final far call, which is why it had been filed as a "fragment" in round 89. */
extern int __near __pascal h1(int c, int d, int a, int b);
extern int __near __pascal h2(int x);
extern int __far __pascal h3(int x, int y);

void __far __pascal f(int a, int b, int c, int d)
{
    h3(h2(h1(c, d, a, b)), 1);
}
