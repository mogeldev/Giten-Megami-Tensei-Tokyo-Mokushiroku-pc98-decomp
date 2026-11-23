char g_2c82;
char g_2c84;

extern int __near __pascal HELP(char __far *, int, int);
extern int __near __pascal HELP_A(int);
extern int __near __pascal HELP_B(int);
extern void __near __pascal HELP6(int, int, int, int, int, int);

int __near __pascal call_a(int a, int b)
{
    return HELP(&g_2c82, a, b);
}

int __near __pascal call_b(int a, int b)
{
    return HELP(&g_2c84, a, b);
}

int __far __pascal two_calls(int a)
{
    HELP_A(-1);
    return HELP_B(a);
}

void __far __pascal six_args(int p0, int p1, int p2, int p3, int p4)
{
    HELP6(p0, p1, p2, p3, 1, p4);
}