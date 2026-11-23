/* Mined single-statement forms, round 34.

   35ca:825a (14 B): 55 8B EC C4 5E 06 26 8B 47 04 C9 CA 04 00
                     -> les bx,[bp+6]; mov ax,es:[bx+4]  = word at offset 4 of a
                        far pointer; 1 far parameter (retf 4)
   35ca:8268 (14 B): same with offset 6
   35ca:8d52 (14 B): same with offset 1
   2603:ccda (16 B): B8 FF FF / 8B 56 06 / 2B C2   -> return -1 - v
   2603:53a0 (18 B): 8A 46 06 / 2A 46 08 / 2C FE / 25 03 00
                     -> return ((a - b) + 2) & 3 with byte parameters
   458e:8e08 (14 B): 8A 46 06 / 25 80 00          -> return v & 0x80 (byte param)
*/
int g_x;

int __far __pascal off4(char __far *p)
{
    return *(int __far *)(p + 4);
}

int __far __pascal off6(char __far *p)
{
    return *(int __far *)(p + 6);
}

int __far __pascal off1(char __far *p)
{
    return *(int __far *)(p + 1);
}

int __far __pascal neg_minus1(int v)
{
    return -1 - v;
}

unsigned __far __pascal wrap3(unsigned char a, unsigned char b)
{
    return ((b - a) + 2) & 3;
}

int __far __pascal test80(unsigned char v)
{
    return v & 0x80;
}
