/* Round-8, /Ox group: swap-and-return around two calls - the old value is kept
 * in SI (`8B 36 <g>` / `8B C6`), which /Os would spill to a frame. */
extern int g_f86;
extern int __far __pascal sub0(void);

int __far __pascal F_2160(int v)
{
    int old;
    old = g_f86;
    g_f86 = v;
    sub0();
    sub0();
    return old;
}

int __far F_TAIL6(int x) { return x; }
