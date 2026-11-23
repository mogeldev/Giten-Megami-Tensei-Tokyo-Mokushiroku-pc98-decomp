/* Round-6: the first row that needs match.py's folded-far-call rule.
 * The image holds a 4-byte `0E E8 rel16` (LINK /F folded a same-segment far
 * call by dropping the NOP), the object still has 5-byte `9A`, so the tail is
 * shifted by one byte. /G0 supplies `8B E5 5D` and `83 EC 04`. */
extern char g_5284;
extern long __far sub5l(int a, int b, int c, int d, int e);

void __far F_13C6(int a, int b, int c, int d, int e)
{
    long r;
    g_5284 = 1;
    r = sub5l(a, b, c, d, e);
    g_5284 = 0;
}
