/* Round-96 harvest: the simplest possible if/else over two far calls. Found by listing
 * the *unclassified* units that are complete (end at a return) rather than by any
 * prologue pattern. */
extern void __far __pascal h1(void);
extern void __far __pascal h2(void);

void __far __pascal F_34B7(int a)
{
    if (!a) h1(); else h2();
}
