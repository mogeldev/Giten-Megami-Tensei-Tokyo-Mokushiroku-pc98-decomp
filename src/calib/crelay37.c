/* Round-25 harvest: the 36e7 shape with a zero constant - relay four
 * parameters, call again with a DGROUP far pointer, the third parameter and 0,
 * then return the third parameter. */
extern char g_3970[];
extern int __far __pascal fc4(int a, int b, int c, int d);
extern int __far __pascal fc3(char __far *p, int a, int b);

int __far __pascal F_509A(int a, int b, int c, int d)
{
    fc4(a, b, c, d);
    fc3(g_3970, c, 0);
    return c;
}
