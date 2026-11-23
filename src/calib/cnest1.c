extern int __near __pascal HELP1(int, int, int, int);
extern void __near __pascal HELP2(int);
extern char __far *__near __pascal WHERE0(int);
extern char __far *__near __pascal WHERE1(int);
extern void __near __pascal SINK3(char __far *, int, int);

void __far __pascal nested4(int x, int y, int z)
{
    HELP2(HELP1(z, 0, x, y));
}

void __far __pascal nested_ptr(int v)
{
    SINK3(WHERE0(0), 0x1F, v & 0x7F);
}

void __far __pascal nested_ptr2(int v)
{
    SINK3(WHERE1(1), 0x0D, v & 0x7F);
}