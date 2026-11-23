/* Canonical far-pascal one-param functions (round 27), all 14 B:
     push bp / mov bp,sp / mov ax,[bp+6] / <op> / leave / retf 2
   Originals:
     35ff:0004  A3 21A4        -> g_21a4 = v;
     3b20:0006  A3 1764        -> g_1764 = v;
     4c9b:000a  A3 2C16        -> g_2c16 = v;
     1fc6:0004  23 06 9B2A     -> g_9b2a &= v;   (and [disp],ax)
     1fc7:0002  23 06 00F6     -> g_00f6 &= v;
   disp16 operands are DGROUP relocations -> RELOCS. */
int g_21a4;
int g_1764;
int g_2c16;
int g_9b2a;
int g_00f6;

void __far __pascal set_21a4(int v)
{
    g_21a4 = v;
}

void __far __pascal set_1764(int v)
{
    g_1764 = v;
}

void __far __pascal set_2c16(int v)
{
    g_2c16 = v;
}

int __far __pascal and_9b2a(int v)
{
    return v & g_9b2a;
}

int __far __pascal and_00f6(int v)
{
    return v & g_00f6;
}
