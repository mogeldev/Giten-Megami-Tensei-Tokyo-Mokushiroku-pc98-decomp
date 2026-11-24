/* Round-39 harvest: a near-Pascal function whose first call returns a far
 * pointer that is used as a struct base. There must be **no local** for the
 * pointer: with a local MSC 7 switches to an ENTER frame; as one nested
 * expression it keeps the pointer in ES:BX and matches. */
struct T { char pad[4]; int f4; };
extern struct T __far * __near __pascal nc(int a, int b);
extern int __near __pascal nc2(int v);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);
extern int __far __pascal h3(int a);

void __near __pascal F_37FC(register int n)
{
    h1(nc2(nc(n, n)->f4));
    h2(n);
    h3(n);
}
