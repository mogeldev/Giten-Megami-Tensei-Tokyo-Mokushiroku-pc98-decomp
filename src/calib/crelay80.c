/* Round-154 harvest: two register locals, declared in the reverse of the natural order.
 *
 * The original assigns the first call's result to DI and the second to SI. MSC gives SI
 * to the first `register` local it sees, so the declaration order has to be reversed -
 * `register int b, a;` - to make `a` land in DI and `b` in SI. The function also returns
 * int 0 rather than void: the original's `33 C0` before the pops is the only thing that
 * distinguishes the two. */
extern int __far __pascal h1(void);
extern int __far __pascal h2(void);
extern void __far __pascal h3(void);
extern void __far __pascal h4(int a, int b);

int __far __pascal F_3E19(void)
{
    register int b, a;

    a = h1();
    b = h2();
    h3();
    h4(a, b);
    return 0;
}
