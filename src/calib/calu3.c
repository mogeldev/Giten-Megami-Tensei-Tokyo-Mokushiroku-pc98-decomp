int __far __pascal classify(int n)
{
    if (n <= -42)
        return -1;
    if (n >= 42)
        return 1;
    return 0;
}
