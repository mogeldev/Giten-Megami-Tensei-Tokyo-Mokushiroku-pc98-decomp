struct Entry {
    signed int key : 11;
    unsigned int flags : 5;
    unsigned char count;
    unsigned char pad;
};
struct Entry g_866e[64];

extern int __near __pascal take_count(int, int);
extern int __near __pascal finish_count(int, int);

int __far __pascal apply_count(int index, int key, int count)
{
    if (g_866e[index].key == key)
        count -= take_count(index, count);
    return finish_count(key, count);
}
