/* Round-165 harvest: a char argument, when the callee declares char.
 *
 * The original loads the global byte with `A0` and pushes AX as it stands - no `cbw`, no
 * `sub ah,ah`. MSC does that when, and only when, the *callee's parameter* is declared
 * `char`: with `int a` it widens by `cbw` (signed) or `sub ah,ah` (cast to unsigned char),
 * and both differ from the image. */
extern int __far __pascal h(char a, int b, int c);
extern char g_9944;

int __far __pascal F_2D49(int a)
{
    return h(g_9944, a, 1);
}
