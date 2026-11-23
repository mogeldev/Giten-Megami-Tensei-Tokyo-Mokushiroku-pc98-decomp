extern int __far *__near WHERE(int);

int __far __pascal f_3883(int a)
{
    return WHERE(a)[6];
}