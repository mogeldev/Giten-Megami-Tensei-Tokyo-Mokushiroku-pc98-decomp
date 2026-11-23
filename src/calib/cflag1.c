/* Flag-Op-Singleton: or byte [0x0F44], 0x40 ; retf — Original 2131:000c.
   C-Form: g_flag |= 0x40; disp16 = DGROUP-Fixup -> RELOCS. */
char g_flag;

void set_flag(void)
{
    g_flag |= 0x40;
}
