/* Round-7 harvest: three argument stores followed by a one-argument call. */
extern int g_9954, g_9956, g_9958;
extern int __far __pascal sub1(int a);

int __far __pascal F_4C96_3A(int a, int b, int c)
{
    g_9954 = a;
    g_9956 = b;
    g_9958 = c;
    return sub1(1);
}
