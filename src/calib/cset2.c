/* Two leaf forms found by mining call-free bodies (round 30):

     1871:37ce (7 B): C7 06 3C 9B 01 00 C3   mov word [0x9B3C],1; retn
                      -> void __near set_9b3c(void) { g_9b3c = 1; }

     35ca:8df8 (6 B): A0 EA 98 2A E4 CB      mov al,[0x98EA]; sub ah,ah; retf
                      -> byte getter with zero extension; far, no arguments
                         int __far get_b98ea(void) { return (unsigned char)g_b98ea; }
   disp16 operands are DGROUP relocations -> RELOCS. */
int g_9b3c;
unsigned char g_b98ea;

void __near set_9b3c(void)
{
    g_9b3c = 1;
}

int __far get_b98ea(void)
{
    return g_b98ea;
}
