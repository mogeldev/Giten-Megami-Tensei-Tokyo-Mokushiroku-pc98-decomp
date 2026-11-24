/* Round-60 harvest: a guarded initialiser chain. Two calls hand out far pointers to
 * the parameters themselves (`&a`, `&b`, `&c`, pushed as SS:BP, so the parameters
 * must be addressable), then a status call whose result decides whether to redo a
 * second call, then a global store and a final call. */
extern int g_4090;
extern int __far __pascal h1(int __far *a, int __far *b);
extern int __far __pascal h2(int __far *a, int __far *b);
extern int __far __pascal h3(int a, int b, int c);
extern int __far __pascal h4(int a, int b, int c);
extern int __far __pascal h5(void);

int __far __pascal F_5116(int a, int b, int c)
{
    register int r;
    h1(&a, &b);
    h2(&b, &c);
    r = h3(a, b, 0);
    if (r >= 0x20) r = h4(0, c, 0);
    g_4090 = 0x0A;
    h5();
    return r;
}
