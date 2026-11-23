/* Round-5: 8086 code generation (/G0). `8B E5 5D` (mov sp,bp; pop bp) is
 * MSC 7's /G0 epilogue for functions that contain a call, so the family that
 * docs/IDIOMS.md listed as an unexplained idiom is plain /G0 output.
 * `33 C0 50` is how /G0 pushes a zero constant. */
extern int __far __pascal sub5(int a, int b, int c, int d, int e);

void __far F_103A(int a, int b, int c, int d) { sub5(0, d, c, b, a); }
