/* Round-28 harvest: an unprototyped far call whose long result is compared with
 * -1L. The missing prototype is what makes MSC clean the arguments with
 * `mov sp,bp` (`8B E5`) instead of `add sp,6`. */
extern long __far h();
extern int __far __pascal h2(char __far *p, int v);
extern char g_013a[];

void __far __pascal F_1FC8(int a)
{
    if (h(a, 0, 0) == -1L) h2(g_013a, 0x4F);
}
