/* Round-3 harvest, /Ox group: call-result combinations, a fastcall relay and
 * the unsigned 32-bit product. /Ox is required for the SI register staging
 * (`8B F0`/`8B C6`) and for the frameless /Ox shapes. */
extern int __far __pascal sub1(int a);
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal suba(void);
extern int __far __pascal sub0b(void);
extern int __near __pascal nvoid(int a);
extern int __near __pascal nret(int a);
extern long __far __pascal LSUB(unsigned long v);
extern int __far __fastcall fsub2(int x);
extern int __far __fastcall fret2(int x);

int __far F_20F4(void)
{
    int x, y;
    x = suba();
    y = sub0b();
    return x | y;
}

int __far __pascal F_2A13(int a) { return (unsigned char)sub1(a); }

int __near __pascal F_2341(register int a)
{
    sub1(a);
    return a;
}

int __far __pascal F_37EC(int a)
{
    sub2(a, 0x8000);
    return -1;
}

void __far __pascal F_3816(int a)
{
    sub1(a);
    nvoid(a);
}

long __far __pascal F_1E55(int a, int b)
{
    return LSUB((unsigned long)(unsigned)a * (unsigned)b);
}

int __far __fastcall F_3DD4(int x)
{
    fsub2(x);
    return fret2(x);
}
