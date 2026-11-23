/* Callback guard through a struct, original 4665:0004 (32 B, near pascal retn 8).

     55 8B EC            push bp; mov bp,sp
     C4 5E 08            les bx,[bp+8]          <- struct far pointer
     26 8B 47 12         mov ax,es:[bx+0x12]    <- the callback's segment
     26 0B 47 10         or  ax,es:[bx+0x10]    <- ... and its offset: null test
     74 0C               je skip
     06 53               push es; push bx       <- the struct pointer as first argument
     FF 76 06 / FF 76 04 push a; push b
     26 FF 5F 10         call far es:[bx+0x10]
     C9 C2 08 00         leave; retn 8

   retn 8 = 4 (far struct pointer) + 2 + 2, and pascal pushes left to right, so the
   struct pointer is the first declared parameter (highest offset).
*/
struct S;

typedef void (__far __pascal *cb_t)(struct S __far *, int, int);

struct S {
    char pad[0x10];
    cb_t fn;
};

void __near __pascal cb_struct(struct S __far *s, int a, int b)
{
    if (s->fn)
        s->fn(s, a, b);
}
