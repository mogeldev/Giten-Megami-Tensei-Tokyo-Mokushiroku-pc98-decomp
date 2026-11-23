extern void (__far __pascal *g_cb)(int, int, int);

void __near __pascal call_cb(int a, int b, int c)
{
    if (g_cb)
        g_cb(a, b, c);
}

int __far __pascal vid_swap(int v)
{
    int old;

    old = *(int __far *)0x48270862L;
    *(int __far *)0x48270862L = v;
    *(unsigned char __far *)0x4827085CL |= 8;
    return old;
}
