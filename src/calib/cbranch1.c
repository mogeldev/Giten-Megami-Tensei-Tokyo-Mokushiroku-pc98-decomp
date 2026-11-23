/* Round 69 - far pointer non-null passthrough, original 4a91:0002 (27 B, MATCH).

     8B 5E 06      mov bx,[bp+6]      <- offset (first declared argument)
     8B 46 08      mov ax,[bp+8]      <- segment
     0B C3         or ax,bx           <- null test on the whole far pointer
     74 05         je zero
     33 C0 / 99    xor ax,ax; cwd     <- return 0
     EB 05         jmp end
   zero: 8B C3 / 8B 56 08             <- return the pointer unchanged
   Needs /Ox: with /Os the null test and the return do not fit this shape. */
char __far *__far __pascal keep_ptr(char __far *p)
{
    if (!p)
        return 0;
    return p;
}