/* Round-239 harvest: a six-parameter pass-through, and the near/far combination that unlocks it.
 *
 * Round 216 transcribed this and was one parameter offset out: with `__far __pascal` the `char`
 * parameter landed at `[bp+10]` instead of `[bp+0E]`. Round 238's tell says the function is
 * **near** (the epilogue is `ret 0C` and the first parameter is at `[bp+0E]`), and with
 * `__near __pascal` the offsets are right.
 *
 * The callee stays **far**: the image's call is `90 0E E8`, which is LINK's `/F` translation of
 * a far call, so the object must contain a `9A`. A near caller with a far callee is an ordinary
 * mixed-model situation, not a workaround. */
extern void __far __pascal h(char a, int b, int c, int d, int e, int f);

void __near __pascal F_2D60(char a, int b, int c, int d, int e, int f)
{
    h(a, b, c, d, e, f);
}
