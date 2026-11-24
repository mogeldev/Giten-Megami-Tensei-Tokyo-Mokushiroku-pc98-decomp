/* Round-35 harvest: three calls nested through AX, with the first parameter in a
 * register so it is pushed from SI twice. */
extern int __far __pascal h1(int a);
extern int __far __pascal h3(int a, int b, int c);

int __far __pascal F_3A4A(register int a, int b)
{
    return h1(h1(h3(a, a, b)));
}
