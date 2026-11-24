/* Round-48 harvest: a two-argument relay whose first argument is itself a
 * two-argument call on the same register value. */
extern int __far __pascal h2(int a, int b);
extern int __far __pascal h2b(int a, int b);

void __far __pascal F_388D_06(register int a)
{
    h2b(h2(a, a), 0);
}
