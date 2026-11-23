/* Flag-op singleton: or byte [0x0F44], 0x40 ; retf — original 2131:000c.
   C form: g_flag |= 0x40; disp16 = DGROUP fixup -> RELOCS. */
char g_flag;

void set_flag(void)
{
    g_flag |= 0x40;
}
