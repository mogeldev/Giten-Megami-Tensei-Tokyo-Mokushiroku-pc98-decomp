#define MK_FP(s, o) ((void __far *)(((unsigned long)(s) << 16) | (unsigned)(o)))

int __far __pascal vid_swap(int v)
{
    int old;

    old = *(int __far *)MK_FP(0x4827, 0x862);
    *(int __far *)MK_FP(0x4827, 0x862) = v;
    *(unsigned char __far *)MK_FP(0x4827, 0x85C) |= 8;
    return old;
}