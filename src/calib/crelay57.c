/* Round-53 harvest: a guard written as `if (call(a) + 1)`, which MSC 7 compiles
 * to `inc ax` / `jz` - the idiom for testing a call result against -1 without a
 * compare. Both branches relay the same register parameter. */
extern int __near __pascal fc(int a);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);

void __far __pascal F_42AC(register int a)
{
    if (fc(a) + 1) h1(a);
    else h2(a);
}
