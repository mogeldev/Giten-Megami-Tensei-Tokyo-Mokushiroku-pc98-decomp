/* Round 83 - "call, read a field through the returned far pointer, call again".

   37fb:0006 (24 B, NEAR pascal retn 2 - note `C9 C2 02 00`, so the argument
     sits at bp+4):
       FF 76 04 / E8 <rel> / 8E C2 / 8B D8 / 26 FF 77 16 / E8 <rel>
     -> SINK(*(int __far *)((char __far *)WHERE(a) + 0x16));

   382c:0002, 3842:0008, 3844:0000 - same shape, FAR pascal (retf 2), offsets
   0x04, 0x1A, 0x1C.

   The important difference to the 3883 family: here MSC's `8E C2 / 8B D8` order
   is the one the binary uses, so these four are reachable.
*/
extern int __far *__near __pascal WHERE(int);
extern void __near __pascal SINK(int);

void __near __pascal chain16(int a)
{
    SINK(*(int __far *)((char __far *)WHERE(a) + 0x16));
}

void __far __pascal chain04(int a)
{
    SINK(*(int __far *)((char __far *)WHERE(a) + 0x04));
}

void __far __pascal chain1a(int a)
{
    SINK(*(int __far *)((char __far *)WHERE(a) + 0x1A));
}

void __far __pascal chain1c(int a)
{
    SINK(*(int __far *)((char __far *)WHERE(a) + 0x1C));
}
