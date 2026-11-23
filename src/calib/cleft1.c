/* Two leftovers from the family sweep (round 61).

   3ded:001c (13 B): 55 8B EC C4 5E 06 26 8B 47 02 C9 CA 04 00
                     -> int __far __pascal f(int __far *p) { return p[1]; }
                        (same accessor family as 3ded:000e, offset +2)
   37f9:000c (10 B): 55 8B EC 8B 46 04 C9 C2 02 00
                     -> int __near __pascal f(int a) { return a; }
                        (near frame: the argument sits at bp+4)
*/
int __far __pascal field1(int __far *p)
{
    return p[1];
}

int __near __pascal ident(int a)
{
    return a;
}
