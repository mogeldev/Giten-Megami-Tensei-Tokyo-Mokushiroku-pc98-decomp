extern void __near __pascal prepare(int);
extern int __near __pascal relay(int, int, int, int, int);
extern int __near __pascal setup(int, int, int, int, int);
extern int __near __fastcall finalize(int, int);

int __near __pascal prep_relay(int a, int b, int c, int d)
{
    register int index = a;
    prepare(index);
    return relay(index, b, c, d, 1);
}

int __far __pascal setup_relay(int a, int b, int c, int d, int e)
{
    register int index = c;
    return finalize(setup(a, b, index, d, e), index);
}
