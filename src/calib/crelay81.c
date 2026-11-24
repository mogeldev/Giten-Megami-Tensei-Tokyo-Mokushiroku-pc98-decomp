/* Round-160 harvest: round 159's "move a parameter into DI" trick, applied.
 *
 * The original keeps the parameter in DI and the call result in SI. MSC gives SI to the
 * first `register` local, so the declaration order is reversed - `register int r, a;` -
 * and `a = a0;` folds into the parameter fetch, giving `57 8B 7E 06` (push di; mov
 * di,[bp+6]) exactly as the original has it. */
extern int __far __pascal h1(int a);
extern int __near __pascal h2(int a);

int __far __pascal F_3A3D(int a0)
{
    register int r, a;

    a = a0;
    r = h1(a);
    h2(a);
    return r;
}
