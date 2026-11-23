int __near __pascal scale64(int a, int b)
{
    register int offset = b;
    offset <<= 6;
    return offset + a;
}
