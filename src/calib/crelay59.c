/* Round-61 harvest: the third member of the address-of-parameter family - three
 * calls exchange far pointers to the parameters themselves, then a status call
 * decides whether a second call reruns. Its twin at 511b:000e matches except for
 * the scratch register (AX vs CX) MSC 7 picks for the third `&b`. */
extern int __far __pascal h1(int __far *a, int __far *b);
extern int __far __pascal h2(int __far *a, int __far *b);
extern int __far __pascal h3(int __far *a, int __far *b);
extern int __far __pascal h4(int a, int b, int c);
extern int __far __pascal h5(int a, int b, int c);
extern int __far __pascal h6(void);

int __far __pascal F_5108(int a, int b, int c)
{
    register int r;
    h1(&a, &b);
    h2(&b, &c);
    h3(&a, &b);
    r = h4(a, b, 1);
    if (r >= 0x20) r = h5(0, c, 0);
    h6();
    return r;
}
