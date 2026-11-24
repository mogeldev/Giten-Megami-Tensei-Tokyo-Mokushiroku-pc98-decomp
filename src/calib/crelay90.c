/* Round-184 harvest: three calls in a row, the last with a negative constant.
 *
 * The function is `__far __pascal` with no parameters - the epilogue is a bare `retf` (CB),
 * which is what distinguishes it from the near cdecl form (whose `ret` differs by one
 * byte). Found by looking at units that begin exactly where a verified row ends, i.e. the
 * next function in the same translation unit. */
extern void __far __pascal h1(void);
extern void __far __pascal h3(void);
extern void __far __pascal h2(int x);

void __far __pascal F_4E75(void)
{
    h1();
    h3();
    h2(-1);
}
