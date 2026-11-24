/* Round-88 harvest: a guarded relay whose long result is forwarded into a near call.
 * Three things had to line up: the parameter in a register (pushed from SI three
 * times), the callee returning a long (DX:AX pushed as a pair), and the tail call
 * being __near (E8) rather than far. */
extern int __near __pascal h1(int a);
extern long __far __pascal h2(int a);
extern int __near __pascal h3(long v, int a);

void __far __pascal F_2193(register int a)
{
    h1(-1);
    h3(h2(a), a);
}
