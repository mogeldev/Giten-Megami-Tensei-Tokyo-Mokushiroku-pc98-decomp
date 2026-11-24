/* Round-135 harvest: the CX-staged selector, which is wall 13 under another name.
 *
 * Two things were needed: the parameters are `(long v, int sel)` - the selector is the
 * *last* parameter, at [bp+06], which is why the original's first instruction reads it -
 * and `/Ox` is required for MSC to cache it in CX the way the original does. Under
 * `/Os` MSC compares the frame slot twice (`83 7E 06`). */
extern int g_4688;
extern char g_46e1[];
extern int __far __pascal h(int a, char __far *p, long v);

long __far __pascal f(long v, int sel)
{
    if (sel == 0x19 || sel == 0x14) {
        g_4688 = sel;
        h(sel == 0x19 ? 0x6C : 0x68, g_46e1, v);
    }
    return v;
}
