struct Entry {
    unsigned int key : 11;
    unsigned int flags : 5;
    unsigned char count;
    unsigned char pad;
};
struct Entry g_876e[64];

void __far clear_entries(void)
{
    struct Entry *p = g_876e;
    do {
        p->key = 2047;
        p->count = 0;
    } while (++p < g_876e + 64);
}

struct Entry __far *__far get_entries(void)
{
    return g_876e;
}
