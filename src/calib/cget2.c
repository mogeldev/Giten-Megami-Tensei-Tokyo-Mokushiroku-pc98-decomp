/* GET-Familie, Teil 2: vier Einzelscalar-Getter (Form A1 <disp16> CB).
   Originale:
     1fd5:0006  -> DGROUP 0x01A4      43a0:000c -> DGROUP 0x2FCE
     4dce:0002  -> DGROUP 0x2C50     4e99:000c -> DGROUP 0x2D0C
   disp16 ist DGROUP-Relocation -> RELOCS. Namen vorlaeufig nach Adresse,
   echte Namen folgen mit Subsystem-Kontext. */
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
