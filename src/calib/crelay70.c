/* Round-103 harvest: a marshalling wrapper with three cdecl calls - one of them far,
 * the other two near - taking the address of its own parameter (far pointer into the
 * stack frame) and passing a near pointer as a far one.  The locals are declared in an
 * order that puts the result slot at [bp-6]. */
extern int __near __cdecl h1(char __far *p);
extern int __far __cdecl h2(char __far *p, int a, int b, char __far *q);
extern int __near __cdecl h3(int t, char __far *p);

int __cdecl f(register char *p, int unused, int a, int b, int c)
{
    register int t;
    int u1, u2, r;

    t = h1((char __far *)p);
    r = h2((char __far *)p, a, b, (char __far *)&c);
    h3(t, (char __far *)p);
    u1 = u2 = 0;
    return r + u1 + u2;
}
