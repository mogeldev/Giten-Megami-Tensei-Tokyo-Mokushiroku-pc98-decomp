/* Round-4 harvest, /Os group. Far calls are LINK /F translations in the image
 * (object side: `9A`). See CONVENTIONS.md. */
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal h1(int a);

int __far __pascal F_31E2(int a, int b) { return h1(sub2(a, b)); }

int __far __pascal F_37EA(int x, int y, int z)
{
    if (x == -1) x = sub2(y, z);
    return x;
}
