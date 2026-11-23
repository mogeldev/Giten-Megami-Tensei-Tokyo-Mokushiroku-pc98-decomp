extern void __near __pascal HELP(int);

void __far six_calls(void)
{
    register int i;

    for (i = 0; i < 6; i++)
        HELP(i);
}