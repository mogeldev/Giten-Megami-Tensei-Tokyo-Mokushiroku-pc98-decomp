/* Round-167 harvest: two calls in sequence, the middle one taking a byte and a constant
 * pointer. The byte pushes as-is because the callee declares `char` (round 165), and the
 * last call takes no argument at all - writing it as `h2(h3(...))` inserts a `push ax`
 * that the image does not have. */
extern int __far __pascal h1(int a);
extern void __far __pascal h2(void);
extern int __far __pascal h3(char a, char *p);
extern char g_1bec;

void __far __pascal F_2DAA(int a)
{
    h1(a);
    h3(g_1bec, (char *)0x1BE8);
    h2();
}
