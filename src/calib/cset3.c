/* Global-initializer family (round 31): far functions without parameters that
   store one immediate into a DGROUP word.

     458e:a206 (7 B): C7 06 39 F8 00 00 CB   mov word [0x39F8],0 ; retf
                      -> resets the slot counter proven in rounds 17/18
     458e:35ae (7 B): C7 06 4E 23 01 00 CB   mov word [0x234E],1 ; retf

   The inventory sizes for both are one byte too long (trailing gap byte).
   disp16 operands are DGROUP relocations -> RELOCS. */
int g_slot_count;
int g_234e;
int g_9a08;
int g_1bac;

void __far reset_slot_count(void)
{
    g_slot_count = 0;
}

void __far init_234e(void)
{
    g_234e = 1;
}

void __far init_9a08(void)
{
    g_9a08 = 1;
}

void __far zero_1bac(void)
{
    g_1bac = 0;
}
