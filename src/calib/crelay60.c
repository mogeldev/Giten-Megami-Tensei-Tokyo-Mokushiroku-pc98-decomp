/* Round-75 harvest: a nested call with the parameter in a register, so it is
 * pushed from SI for the inner call and the result is pushed straight into the
 * outer one. */
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);

void __far __pascal F_32DA(register int a)
{
    h2(h1(a));
}
