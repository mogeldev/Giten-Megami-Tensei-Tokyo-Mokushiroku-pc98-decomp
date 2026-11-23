/* Three frameless getters/updaters fused into a 20-byte unit, 3e24:006c:

     A1 B0 1B CB                  mov ax,[0x1BB0]; retf       (4 B)
     FF 06 B0 1B A1 B0 1B CB      inc [0x1BB0]; mov ax,[..]; retf (8 B)
     FF 0E B0 1B A1 B0 1B CB      dec [0x1BB0]; mov ax,[..]; retf (8 B)

   Note for tools/split.py: these units are frameless, terminate with a bare CB
   and do not begin with a frame prologue, so the current split rule does not
   separate them - the unit only surfaced because none of the three parts calls
   or jumps. Widening the splitter to bare-CB terminators is a known gap.
*/
int g_1bb0;

int __far get_1bb0(void)
{
    return g_1bb0;
}

int __far inc_get_1bb0(void)
{
    g_1bb0++;
    return g_1bb0;
}

int __far dec_get_1bb0(void)
{
    g_1bb0--;
    return g_1bb0;
}
