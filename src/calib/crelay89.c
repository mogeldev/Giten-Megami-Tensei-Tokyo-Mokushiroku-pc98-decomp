/* Round-175 harvest: the round-174 hypothesis, applied.
 *
 * MSC zeroes AX with `2B C0` (`sub ax,ax`) when the zero is the source of a wider store,
 * so a `long` global cleared to zero produces `2B C0` followed by the two word stores -
 * exactly the image. The same construct with a plain int would use `33 C0`, which is why
 * this only works inside the wider-integer context. */
extern int __near __cdecl h(void);
extern int g_536e;
extern long g_9650;

void __near __cdecl F_1AB9(void)
{
    g_536e = h();
    g_9650 = 0;
}
