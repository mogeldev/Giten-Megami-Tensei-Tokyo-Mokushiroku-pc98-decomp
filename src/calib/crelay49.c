/* Round-42 harvest: two two-argument relays back to back. */
extern void __far __pascal h1(int a, int b);
extern void __far __pascal h2(int a, int b);

void __far __pascal F_2D3A(int a, int b, int c, int d)
{
    h1(c, d);
    h2(a, b);
}
