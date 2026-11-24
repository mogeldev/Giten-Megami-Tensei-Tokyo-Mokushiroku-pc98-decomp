/* Round-78 harvest: a near-Pascal function forwarding a scaled integer. */
extern int __far __pascal h(int a);

void __near __pascal F_486E(int a, int b)
{
    h(a * b / 100);
}
