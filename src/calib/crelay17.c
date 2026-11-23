/* Round-7 harvest, /Ox group: four near-Pascal calls with descending constants,
 * then a far call - the `register` parameter keeps the argument in SI so every
 * push is `push si` (`56`), which is what the original does.
 * The trailing F_TAIL4 only exists so the last symbol can be sliced. */
extern int __far __pascal sub1(int a);
extern int __near __pascal nsub2(int a, int b);

void __near __pascal F_22FE(register int a)
{
    nsub2(a, 3);
    nsub2(a, 2);
    nsub2(a, 1);
    nsub2(a, 0);
    sub1(a);
}

int __far F_TAIL4(int x) { return x; }
