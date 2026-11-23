char g_2c82;
char g_2c84;

extern int __near __pascal HELP5(int, int, int, int, int);
extern void __near __pascal HELP(char __far *, int, int, char);

int __near __pascal five_zeros(int a)
{
    HELP5(a, 0, 0, 0, 0);
    return 0;
}

void __near __pascal dgroup_call(int a, int b, char c)
{
    HELP(&g_2c82, a, b, c);
}

void __near __pascal dgroup_call2(int a, int b, char c)
{
    HELP(&g_2c84, a, b, c);
}