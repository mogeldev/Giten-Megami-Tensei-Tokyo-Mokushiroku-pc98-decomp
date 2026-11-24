/* Round-47 harvest: a four-case switch returning the callee's long result.
 * The `default:` clause must be written **first**: MSC then lays the default block
 * out directly after the compare chain (as the original does) and the case blocks
 * follow. With `default:` last the block order - and every branch distance -
 * changes. */
extern long __far __pascal h1(int a, int b, int c);
extern long __far __pascal h2(int a, int b, int c);
extern long __far __pascal h3(int a, int b, int c);
extern long __far __pascal h4(int a, int b, int c);

long __far __pascal F_1F5F(int a, int b, int c, int x)
{
    switch (x) {
    default: return ((long)a << 16) | (unsigned)b;
    case 0: return h1(a, b, c);
    case 1: return h2(a, b, c);
    case 2: return h3(a, b, c);
    case 3: return h4(a, b, c);
    }
}
