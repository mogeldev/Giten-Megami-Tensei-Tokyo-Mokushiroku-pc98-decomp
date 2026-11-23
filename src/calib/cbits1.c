int __far __pascal twobits(int __far *p)
{
    int r;

    r = (*p == 0);
    r |= (p[2] == 0) ? 2 : 0;
    return r;
}
