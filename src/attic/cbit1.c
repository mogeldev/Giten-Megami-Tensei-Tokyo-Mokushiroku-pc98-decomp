/* Bit set in a byte table, original 2603:463c (38 B, far pascal, retf 2):
     55 8B EC        push bp; mov bp,sp
     56              push si
     8B 76 06        mov si,[bp+6]       ; n
     8B DE           mov bx,si
     8B C6           mov ax,si
     99              cwd
     83 E2 07        and dx,7            ; sign fixup for sar
     03 C2           add ax,dx
     C1 F8 03        sar ax,3            ; n / 8
     83 E3 07        and bx,7            ; n & 7
     8B F0           mov si,ax
     8A 87 42 00     mov al,[bx+0x0042]  ; bit table in DGROUP
     08 84 76 5E     or  [si+0x5E76],al ; target table
     5E              pop si
     C9 CA 02 00     leave; retf 2

   -> table[n / 8] |= bit_table[n & 7];
   The signed shift explains the cwd/and/add fixup sequence. */
unsigned char bit_table[8] = { 1, 2, 4, 8, 16, 32, 64, 128 };
unsigned char g_5e76[64];

void __far __pascal set_bit(int n)
{
    g_5e76[n / 8] |= bit_table[n & 7];
}
