/* Wrapper function, original 37ce:000c (13 B):
     55 8B EC          push bp; mov bp,sp
     FF 76 04          push word [bp+4]     <- first (only) argument, near pascal
     E8 C3 FF          call inner           (rel16 - relocation)
     C9                leave
     C2 02 00          retn 2               (callee pops the argument)
   So the callee cleans up as well: pascal convention on both sides. */
extern void __near __pascal inner_37ce(int a);

void __near __pascal wrap_37ce(int a)
{
    inner_37ce(a);
}
