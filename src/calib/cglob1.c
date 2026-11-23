int g_1b12;
int g_1b14;

int __far cmp_globals(void)
{
    int r;

    if (g_1b12 <= g_1b14)
        r = 0;
    else
        r = 1;
    return r;
}