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

int __near __pascal take_counts(int key, int count)
{
    register int index = 63;
    register struct Entry *entry = g_866e + 63;

    do {
        if (entry->key == key) {
            count -= take_count(index, count);
            if (count <= 0)
                break;
        }
        --index;
        /* Match the original 16-bit DGROUP offset comparison, including
           the final step before the table. That offset is not dereferenced. */
        --entry;
    } while (entry >= g_866e);
    return count;
}
