/* Round-14 harvest: a long-argument helper with two branches. Note that two
 * *distinct* callees are required here: with a single callee MSC merges the two
 * call sequences into a tail jump (`EB E8`), which the original does not have. */
extern long __far __pascal lfc1(long v, int n);
extern long __far __pascal lfc2(long v, int n);

long __far __pascal F_1F57(long v, int n)
{
    if (n < 0) return lfc1(v, -n);
    if (n > 0) return lfc2(v, n);
    return v;
}
