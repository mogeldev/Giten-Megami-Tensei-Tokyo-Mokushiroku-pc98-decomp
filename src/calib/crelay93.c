/* Round-203 harvest: the first half of a unit the inventory mis-cut.
 *
 * `1ab4:000c` is inventoried as one 72-byte function, but it contains a `ret` at offset 0x1A
 * with a second function's code after it, so the window spans two functions. The first is
 * 27 bytes and matches:
 *
 * The two `long` globals are cleared with `2B C0` plus four word stores, and `if (g_536c)`
 * compares AL (already zero) against the byte rather than comparing the byte with an
 * immediate - which is why the head has no `80 3E`. */
extern char g_536c;
extern int g_536e;
extern long g_9950, g_9b18;

void __near __cdecl F_1AB4(void)
{
    g_9950 = 0;
    g_9b18 = 0;
    if (g_536c) g_536e = -1;
}
