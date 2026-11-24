/* Round-260 harvest: a freshly allocated six-byte record, zeroed through a far pointer.
 *
 * `p->a = p->b = p->c = 0` stores the zero as three immediates (`26 C7 47 xx 00 00`), which is
 * what the original does NOT do: it zeroes AX once (`2B C0`) and stores the register three
 * times. Round 175's rule - a zero stored wider than AX makes MSC use `sub ax,ax` - reaches it:
 * clear the first four bytes as a `long`, then the remaining word. Both MSC 7.0 and 6.0 give the
 * same object, so no toolchain selector is needed.
 *
 * The allocator takes (1, 6): the image pushes 01 then 06, i.e. declaration order under pascal. */
struct S { int a, b, c; };
extern struct S far * far pascal alloc(int kind, int size);

struct S far * far pascal F_2B2E(void)
{
    struct S far *p;

    p = alloc(1, 6);
    *(long far *)&p->a = 0;
    p->c = 0;
    return p;
}
