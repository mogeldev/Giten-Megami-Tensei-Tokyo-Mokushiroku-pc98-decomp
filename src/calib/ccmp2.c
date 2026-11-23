int g_2d02, g_2d04, g_2d06, g_2d08, g_2d0a;

int __near __pascal compare_config(int a, int b, int c, int d, int e, int check_e)
{
    if (g_2d06 != c || g_2d08 != d || g_2d02 != a || g_2d04 != b)
        goto mismatch;
    if (check_e && g_2d0a != e)
        return 1;
    return 0;
mismatch:
    return -1;
}
