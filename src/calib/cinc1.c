/* Geschwister-Paar am Globalen DGROUP 0x39F8 (beide __near):
     4fab:000a (15 B): cmp g,0x10 / jl->load / mov ax,-1 / jmp / mov ax,[g] / ret
                        -> return (g < 0x10) ? g : -1;   (Ternaer, ein Exit)
     4fac:000a (11 B): cmp g,0x10 / jge +4 / inc g / ret
                        -> if (g < 0x10) g++;
   Vorzeichen: jl/jge = signed int. disp16 = Fixups -> RELOCS. */
int g_39f8;

int __near get_39f8_clamped(void)
{
    return (g_39f8 >= 0x10) ? -1 : g_39f8;
}

void __near inc_39f8_capped(void)
{
    if (g_39f8 < 0x10)
        g_39f8++;
}
