/* Round-84 harvest: a guarded initialiser. The cdecl call's arguments are written in
 * the reverse of the push order (round 79's rule) and the guard runs a two-argument
 * far call with a DGROUP object pointer. */
extern int __cdecl cd(int a, int b);
extern char g_4668[];
extern int __far __pascal h2b(int a, char __far *p);

int __far __pascal F_1EBD(int a, int b)
{
    if (cd(b, a)) h2b(1, g_4668);
    return 1;
}
