struct S {
    char pad[0x1E];
    int f;
};

extern struct S __far *__near __pascal WHERE(int);

int __far __pascal bits3(int a)
{
    return (WHERE(a)->f << 13) >> 15;
}