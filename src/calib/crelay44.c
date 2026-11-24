/* Round-36 harvest: two far-pointer stores of the same call result, with the
 * argument in a register so it is pushed from SI twice. */
extern int __far __pascal h(int x);

void __far __pascal F_388D(register int x, int __far *a, int __far *b)
{
    *a = h(x);
    *b = h(x);
}
