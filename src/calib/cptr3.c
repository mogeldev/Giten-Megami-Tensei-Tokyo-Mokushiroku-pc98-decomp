/* Copy a pair of words out of a global far pointer, original 458e:5e66 (35 B):
     C4 1E 0A 2B  les bx,[0x2B0A]      ; global far pointer
     26 8B 47 1A  mov ax,es:[bx+0x1A]
     C4 5E 0A     les bx,[bp+0xA]      ; first declared argument
     26 89 07     mov es:[bx],ax
     C4 1E 0A 2B  les bx,[0x2B0A]      ; reloaded: the previous les clobbered BX
     26 8B 47 1C  mov ax,es:[bx+0x1C]
     C4 5E 06     les bx,[bp+6]        ; last declared argument
     26 89 07     mov es:[bx],ax
     C9 CA 08 00  leave; retf 8
   The double load of the global is the natural result of BX being reused. */
int __far *g_2b0a;

void __far __pascal copy_pair(int __far *a, int __far *b)
{
    *a = ((int __far *)g_2b0a)[13];
    *b = ((int __far *)g_2b0a)[14];
}
