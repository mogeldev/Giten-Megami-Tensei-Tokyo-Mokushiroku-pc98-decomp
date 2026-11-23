/* Not a units.csv boundary: the splitter started this unit two bytes late, at
   the fragment 3d59:000e. The real function begins at 3d59:000c, directly after the
   previous function's `retf` plus one padding byte. */
extern void __near __pascal NEXT(int, int);

void __far __pascal relay2(int a, int b)
{
    NEXT(a, b);
}