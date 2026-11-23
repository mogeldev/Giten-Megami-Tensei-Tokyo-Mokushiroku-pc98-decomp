/* Sibling pair at global DGROUP 0x39F8 (both __near):
     4fab:000a (16 B): cmp [g],0x10 / jl +5 / mov ax,-1 / jmp +3
                       / mov ax,[g] / ret
                       -> if/else with ONE common exit (jump merge)
     4fac:000a (12 B): cmp [g],0x10 / jge +4 / inc [g] / ret
   /Os /Oy: no frame, no pointer-omission cost -> the local result
   variable stays in the register and the exit is merged. */
int g_39f8;

int __near get_39f8_clamped(void)
{
    int r;

    if (g_39f8 < 0x10)
        r = g_39f8;
    else
        r = -1;
    return r;
}

void __near inc_39f8_capped(void)
{
    if (g_39f8 < 0x10)
        g_39f8++;
}
