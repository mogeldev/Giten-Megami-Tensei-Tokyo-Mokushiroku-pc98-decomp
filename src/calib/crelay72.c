/* Round-111 harvest: a nested relay that was verified in round 86 but never written
 * into the ledger - it was the third of three matches that round and only two were
 * added. Re-matching it now reproduces it byte-for-byte. */
extern int __far __pascal hd(int a, int b, int c, int d);
extern int __far __pascal he(int a, int b);

void __far __pascal f(int a, int b, int c, int d)
{
    he(hd(a, b, c, d), 0);
}
