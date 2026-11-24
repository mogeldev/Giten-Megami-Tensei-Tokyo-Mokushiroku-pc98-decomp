/* Round-170 harvest: a guarded chain of calls whose value is returned.
 *
 * All four callees are far (`__far __pascal`); making any of them near breaks the call
 * encoding. The if-body ends with `return h3(1, 0);`, which is why the else path is the one
 * that needs the `33 C0` and the body reaches the epilogue with a jump. */
extern int __far __pascal h1(int a);
extern void __far __pascal h4(int x);
extern int __far __pascal h2(int x);
extern int __far __pascal h3(int x, int y);

int __far __pascal F_4DF7(int a)
{
    if (h1(a)) {
        h4(0);
        h2(1);
        return h3(1, 0);
    }
    return 0;
}
