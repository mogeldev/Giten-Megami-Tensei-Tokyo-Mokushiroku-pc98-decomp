/* Round-115 harvest: a long parameter guard. The zero test is a word-OR of the two
 * halves (`8B 46 0A` / `0B 46 08`), the long global is decremented as a word pair
 * (`83 2E <g> 01` / `83 1E <g+2> 00`), and the no-argument call is near while the two
 * long-taking calls are far. */
extern void __near __pascal h0(void);
extern int __far __pascal h1(long v);
extern int __far __pascal h2(long v, int c);
extern long g_40b4;

void __far __pascal f(long v, int c)
{
    if (!v) { h0(); return; }
    if (h1(v)) { h2(v, c); g_40b4--; }
}
