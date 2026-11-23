extern char g_866e[], g_886e[];
extern int __far __pascal scan_a(int, int, int, int, char __far *);
extern int __far __pascal scan_b(int, int, int, int, char __far *);

int __far __pascal scan64_a(int a, int b)
{
    return 64 - scan_a(a, b, 64, 4, g_866e);
}

int __far __pascal scan64_b(int a, int b)
{
    return 64 - scan_b(a, b, 64, 4, g_866e);
}

int __far __pascal scan16_a(int a, int b)
{
    return 16 - scan_a(a, b, 16, 4, g_886e);
}

int __far __pascal scan16_b(int a, int b)
{
    return 16 - scan_b(a, b, 16, 4, g_886e);
}
