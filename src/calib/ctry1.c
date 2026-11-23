extern int __near __pascal first(int);
extern int __near __pascal second(int);
extern int __near __pascal third(int, int);

int __far __pascal dispatch(int v)
{
    register int arg = v;
    if (first(arg) != -1)
        return second(arg);
    return third(arg, 3);
}
