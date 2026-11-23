extern int __near __pascal HELP_A(int);
extern int __near __pascal HELP_B(int);
extern void __near __pascal HELP_V(void);

int __far __pascal plus20(int a)
{
    return HELP_A(a) + 0x14;
}

int __near __pascal nested(int a)
{
    return HELP_B(HELP_A(a));
}

int __far __pascal clear_bit1(char __far *p)
{
    *p &= ~1;
    HELP_V();
    return 1;
}