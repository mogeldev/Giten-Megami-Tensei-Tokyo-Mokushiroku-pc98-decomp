/* Five wrappers inside one 120-byte inventory entry, original 31e3:000c.
   The units are 21 + gap, repeated four times, then a 32-byte conditional:

     55 8B EC          push bp; mov bp,sp
     FF 76 08          push [bp+8]        <- first declared argument (pascal)
     68 00 10          push 0x1000        <- differs per sibling
     FF 76 06          push [bp+6]        <- last declared argument
     9A EC 25 CA 25    callf 25CA:25EC    (relocation)
     C9 CA 04 00       leave; retf 4

   -> the callee is a far pascal function of three word arguments which the
   wrapper calls as  ext(a, <const>, b).

   The fifth unit tests the second parameter:
     83 7E 06 01       cmp word [bp+6],1
     75 0B             jne else
     FF 76 08 / callf 25CA:2674
     EB 09 90          jmp end
     FF 76 08 / callf 25CA:269C
     C9 CA 04 00
   -> if (b == 1) f1(a); else f2(a);
*/
extern void __far __pascal f_25ec(int a, int b, int c);
extern void __far __pascal f_2674(int a);
extern void __far __pascal f_269c(int a);

void __far __pascal w_1000(int a, int b)
{
    f_25ec(a, 0x1000, b);
}

void __far __pascal w_2000(int a, int b)
{
    f_25ec(a, 0x2000, b);
}

void __far __pascal w_8000(int a, int b)
{
    f_25ec(a, 0x8000, b);
}

void __far __pascal w_4000(int a, int b)
{
    f_25ec(a, 0x4000, b);
}

void __far __pascal w_cond(int a, int b)
{
    if (b == 1)
        f_2674(a);
    else
        f_269c(a);
}
