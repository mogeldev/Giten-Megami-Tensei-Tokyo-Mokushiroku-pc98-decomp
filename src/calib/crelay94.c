/* Round-232 harvest: a long shift-left loop, and a genuine MATCH.
 *
 * `1 << n` computed by repeated doubling of a `long` local. Worth noting *why* this one matches
 * when so many near-misses do not: the shift is already a `D1`/`D16` pair in both compilers,
 * so the doubling wall (which is about `add reg,reg`) does not apply, and there is no pad byte,
 * no register-cached parameter and no BX. It needs `/Ox` - under `/Os` MSC keeps the counter in
 * the frame and the shape diverges at the first instruction. */
long __far __pascal F_2A87(int n)
{
    long r;

    r = 1;
    while (n > 0) { r <<= 1; n--; }
    return r;
}
