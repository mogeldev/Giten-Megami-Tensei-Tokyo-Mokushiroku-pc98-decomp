/* Round-122 harvest: two shapes that need no frame at all.
 *
 * `F_37EC` keeps the parameter in SI and returns it unchanged on one path.
 * `F_438C` keeps it in SI and compares the call result directly, so declaring a local
 * for the result (the obvious transcription) forces a frame that the original never
 * has - the `return -1` path shows that no local exists. */
extern int __far __pascal h1(int a);
extern int __near __pascal h2(int a);

int __far __pascal F_37EC(register int a)
{
    if (a == -1) return a;
    h1(a);
    return h2(a);
}

extern int __far __pascal h3(int a);
extern int g_2fce;

int __near __pascal F_438C(register int x)
{
    if (h3(x) == 9) return x - g_2fce;
    return -1;
}
