extern int __near __pascal lookup_a(int);
extern int __near __pascal lookup_b(int);
extern int __near __pascal apply_a(int, int);
extern int __near __pascal apply_b(int, int);

int __far __pascal table_relay_a(int key, int value)
{
    register int index = key;
    return apply_a(lookup_a(index), value);
}

int __far __pascal table_relay_b(int key, int value)
{
    register int index = key;
    return apply_b(lookup_b(index), value);
}
