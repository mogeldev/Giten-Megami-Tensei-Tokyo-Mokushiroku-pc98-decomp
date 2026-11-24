/* Round-77 harvest: a near-Pascal function that stores a call's result back into
 * its own last parameter and then forwards it. The `ret imm16` (`C2 06 00`) is the
 * tell that the function is near, not far - reading it as `CA` shifts every
 * parameter offset by two. */
extern int __near __pascal nc(int a, int b, int c);
extern int __far __pascal h2(int a, int b);

void __near __pascal F_4DB8(int a, int b, int c)
{
    c = nc(a, b, c);
    h2(c, 0);
}
