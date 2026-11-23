/* GET family, part 2: four single-scalar getters (form A1 <disp16> CB).
   Originals:
     1fd5:0006  -> DGROUP 0x01A4      43a0:000c -> DGROUP 0x2FCE
     4dce:0002  -> DGROUP 0x2C50     4e99:000c -> DGROUP 0x2D0C
   disp16 is a DGROUP relocation -> RELOCS. Names provisional by address,
   real names follow with subsystem context. */
int g_01a4;
int g_2fce;
int g_2c50;
int g_2d0c;

int get_1a4(void)
{
    return g_01a4;
}

int get_2fce(void)
{
    return g_2fce;
}

int get_2c50(void)
{
    return g_2c50;
}

int get_2d0c(void)
{
    return g_2d0c;
}
