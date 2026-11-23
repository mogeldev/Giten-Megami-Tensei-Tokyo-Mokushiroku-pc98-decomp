extern int __near __pascal HELP(int);

void __near __pascal upd(int seg, int off)
{
    int __far *p;

    p = (int __far *)(((unsigned long)seg << 16) | (unsigned)off);
    *p = HELP(*p);
}