/* Kalibrier-Familie zu FUN_35ca_8090..809c (DDS98.EXE 35ca:8090):
   vier Far-Getter auf aufeinanderfolgende int-Globals in DGROUP.
   Original-Bytes: A1 <disp16> CB  (mov ax,[disp]; retf), disp = 0x78c6+2*i.
   disp16 ist eine DGROUP-Relocation -> RELOCS-Kandidat, nicht MATCH. */
int g_arr[4] = {0, 0, 0, 0};

int get0(void)
{
    return g_arr[0];
}

int get1(void)
{
    return g_arr[1];
}

int get2(void)
{
    return g_arr[2];
}

int get3(void)
{
    return g_arr[3];
}
