/* Round-33 harvest: three calls in a row with the same argument. The parameter
 * must be `register` so it is pushed from SI three times instead of being
 * reloaded from the frame each time. */
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);
extern int __far __pascal h3(int a);

void __far __pascal F_31F1(register int a)
{
    h1(a);
    h2(a);
    h3(a);
}
