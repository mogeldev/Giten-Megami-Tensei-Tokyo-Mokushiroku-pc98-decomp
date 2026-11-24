/* Round-41 harvest: a six-argument far call whose result is negated with
 * `1 - x` (`48 F7 D8` = dec/neg), with a DGROUP object pointer as the last
 * argument. */
extern char g_98e4[];
extern int __far __pascal h6(int a, int b, int c, int d, char __far *p);

int __far __pascal F_3E7F(int a, int b)
{
    return 1 - h6(a, b, 1, 0x10, g_98e4);
}
