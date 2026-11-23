/* Family: two identical 22-byte functions (round 25)
     352a:0004 = 2603:f274  and  4527:000a = 35ca:f5da
   Original:
     C7 06 30 9B 00 00   mov word [0x9B30], 0
     C7 06 42 9B 00 00   mov word [0x9B42], 0
     6A 01               push 1
     6A 18               push 0x18
     9A d8 83 71 08      call far 0871:83D8
     C3                  retn
   C form: g1 = 0; g2 = 0; p(1, 0x18);   (pascal: left->right, callee cleans up)

   STATUS: PENDING — no MSC-7.0 flag combination hits both traits:
     /G1 /AM /Gs /Os|/Ot|/Ox  -> 33 C0 / A3 / A3   (8 B, zero fold, frameless)
     /G1 /AM /Gs /O2          -> C7 06 x2          (12 B, but with frame)
   The original has C7-06 stores AND no frame. Consistent with the binary
   statistics (add bx,bx 74x vs shl 18x; C7-06 zero 130x vs zero fold 32x),
   this points to an older compiler generation (MSC 6.x) for the game modules.
   Next step: obtain MSC 6.0 and repeat the calibration with it. */
int g_9b30;
int g_9b42;

extern void __far __pascal p_83d8(int a, int b);

void __near reset_9b30(void)
{
    g_9b30 = 0;
    g_9b42 = 0;
    p_83d8(1, 0x18);
}

void __near reset_9b30b(void)
{
    g_9b30 = 0;
    g_9b42 = 0;
    p_83d8(1, 0x18);
}
