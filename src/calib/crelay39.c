/* Round-29 harvest: a flag-guarded six-argument relay. Three details decide it:
   the callee is cdecl (arguments pushed right to left, caller does not pop),
   the build uses G0 (the epilogue is mov sp,bp plus pop bp, not leave), and the
   source assigns the call to a long local that is never read - that local is
   what reserves the four bytes behind the initial sub sp,4. */
extern char g_5284;
extern int __cdecl h6(int a, int b, int c, int d, int e, int f);

void __far F_13AD(int a, int b, int c, int d, int e, int f)
{
    long r;
    g_5284 = 1;
    r = h6(a, b, c, d, e, f);
    g_5284 = 0;
}
