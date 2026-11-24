/* Round-201 harvest: two `long` locals, one of them zeroed.
 *
 * `z = 0` on a `long` local produces `2B C0` plus two word stores (round 175's rule), which
 * is why this unit carries the "sub ax,ax zeroing" fingerprint. It needs `/Ox`: under `/Os`
 * MSC allocates the two longs in the opposite frame order (`[bp-4]`/`[bp-2]` before
 * `[bp-8]`/`[bp-6]`), which shifts every following store by two bytes. */
extern long __far __pascal h1(void);
extern long __far __pascal h2(void);
extern void __far __pascal h3(int a, long r, long z);

void __far __pascal F_2E76(int a, int sel)
{
    long r, z;

    r = h1();
    z = 0;
    if (sel == 1) z = h2();
    h3(a, r, z);
}
