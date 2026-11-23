extern void __near __pascal helper1(int);
extern void __near __pascal helper5(int, int, int, int, int);

void __far relay_minus_one(void)
{
    helper1(-1);
}

void __near relay_defaults(void)
{
    helper5(0, 0, 63, 63, 255);
}
