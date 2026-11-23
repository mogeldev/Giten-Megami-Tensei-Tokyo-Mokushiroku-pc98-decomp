struct Packed {
    signed int value : 14;
    unsigned int flags : 2;
};

struct Packed g_9971;
int g_2b0e, g_2b10;

int __far __pascal swap_value(int value)
{
    int old = g_9971.value;
    g_9971.value = value;
    return old;
}

void __far __pascal store_if(int a, int b)
{
    int first = a;
    if (first != -1)
        g_2b0e = first;
    if (b != -1)
        g_2b10 = b;
}
