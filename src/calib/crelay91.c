/* Round-185 harvest: a local struct passed twice by far pointer, with its field read back.
 *
 * `return s.x;` after the call is what makes the difference: without it the epilogue goes
 * straight to `leave`, but the original reloads the field into AX first. The frame is
 * fourteen bytes (`enter 0x0E, 0`), which is the struct's size, so the struct is exactly
 * `int x; char pad[12];`. */
struct S { int x; char pad[0x0C]; };
extern void __far __pascal h(struct S __far *a, struct S __far *b, int v);

int __far __pascal F_1EC0(void)
{
    struct S s;

    s.x = 0;
    h(&s, &s, 0x33);
    return s.x;
}
