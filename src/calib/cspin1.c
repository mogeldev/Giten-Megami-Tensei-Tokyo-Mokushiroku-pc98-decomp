extern int g_6e4;

void __far spin_wait(void)
{
    while (g_6e4 != 0)
        ;
}