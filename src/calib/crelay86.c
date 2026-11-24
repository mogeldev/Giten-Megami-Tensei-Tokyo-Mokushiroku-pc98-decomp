/* Round-169 harvest: two byte globals pushed with different widening in one call.
 *
 * The first argument is zero-extended (`A0 <g>` / `2A E4` / `50`) and the second is not
 * (`A0 <g>` / `50`). That happens when the callee's first parameter is `int` (so the
 * unsigned char is converted) and its second is `char` (so no conversion is needed) - one
 * prototype explaining both. */
extern int __far __pascal h1(int a, char b, int c, int d, int e);
extern int __far __pascal h2(int x, int y);
extern unsigned char g_995b;
extern char g_995c;
extern int g_9954, g_9956, g_9958;

void __far __pascal F_4C9C(void)
{
    h1(g_995b, g_995c, g_9954, g_9956, g_9958);
    h2(1, 1);
}
