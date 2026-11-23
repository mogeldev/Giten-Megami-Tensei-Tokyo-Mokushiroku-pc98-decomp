/* Array-index accessor, original 35ca:2306 (16 B, near pascal, retn 2):
     8B 5E 04   mov bx,[bp+4]        <- the single word argument
     03 DB      add bx,bx           <- index * 2   (ADD form, not SHL)
     8B 87 2A 14 mov ax,[bx+0x142A]  <- base 0x142A
     C9 C2 02 00 leave; retn 2

   The multiply-by-two appears as `add bx,bx` (03 DB), which is the same shape
   that blocks the CONV pending (4fad:0006). Flag matrix is being tested here. */
int g_142a[256];

int __near __pascal idx_142a(int i)
{
    return g_142a[i];
}
