/* Conditional swap through far pointers, original 2603:452e (34 B, MATCH):
     55 8B EC        push bp; mov bp,sp
     57              push di
     C4 7E 06        les di,[bp+6]      ; last declared argument
     C5 5E 0A        lds bx,[bp+0xA]    ; first declared argument (clobbers DS)
     8B 07           mov ax,[bx]
     26 39 05        cmp es:[di],ax     ; *b - *a
     7D 0A           jge skip           ; swap only when *b < *a
     8B C8           mov cx,ax
     26 8B 05        mov ax,es:[di]
     89 07           mov [bx],ax
     26 89 0D        mov es:[di],cx
     16 1F           push ss / pop ds   ; DS restored after the lds
     5F              pop di
     C9 CA 08 00     leave; retf 8

   Per-file flags: /Ox reproduces this register-only form; /Os and /Ot spill the
   temporary to the stack (ENTER 2) and produce a different frame. */
void __far __pascal swap_if_lt(int __far *a, int __far *b)
{
    int t;

    if (*b < *a) {
        t = *a;
        *a = *b;
        *b = t;
    }
}
