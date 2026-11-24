/* Round-86 harvest: two more pure relays. Both units carry a padding byte in the
 * inventory, so the row sizes are one less than the unit size. */
extern int g_2e2a;
extern char g_860e[];
extern int __far __pascal hb(char __far *p, int a);

void __far __pascal F_4F5C(int a)
{
    g_2e2a = 0;
    hb(g_860e, a);
}

extern int __far __pascal hd(int a, int b, int c, int d);
extern int __near __pascal nf(int a);

int __far __pascal F_3BD6(int a, int b, int c, int d)
{
    hd(a, b, c, d);
    nf(c);
    return c;
}
