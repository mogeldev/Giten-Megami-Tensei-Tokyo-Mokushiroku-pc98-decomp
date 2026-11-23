/* Round-12 harvest: framed wrappers whose arguments are passed in AX (fastcall)
 * or stored through far pointers. */
extern int __far __fastcall fc1(int a);
extern char __far __pascal csub(void);

void __far __pascal F_3E19_24(int a, int b)
{
    fc1(0x0D);
    fc1(a);
    fc1(b);
}

void __far __pascal F_2E39(int __far *p1, int __far *p2)
{
    *p1 = (unsigned char)csub();
    *p2 = (unsigned char)csub();
}
