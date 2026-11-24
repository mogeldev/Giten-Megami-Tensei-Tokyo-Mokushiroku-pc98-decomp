/* Round-79 harvest: a cdecl call whose result is incremented and forwarded.
 * cdecl pushes right to left, so the source argument order is the reverse of the
 * push order the original shows - `cd(b, a)` produces `push a` / `push b`. */
extern int __cdecl cd(int a, int b);
extern int __far __pascal h2(int a);

void __far __pascal F_1DFC(int a, int b)
{
    h2(cd(b, a) + 1);
}
