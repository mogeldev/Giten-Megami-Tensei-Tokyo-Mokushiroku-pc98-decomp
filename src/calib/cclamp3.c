int g_4688;
int g_468a;

int __near __fastcall clamp_4688(int v)
{
    if (v < 1)
        return 1;
    if (v > g_4688)
        return g_4688;
    return v;
}

int __near __fastcall clamp_468a(int v)
{
    if (v < 1)
        return 1;
    if (v > g_468a)
        return g_468a;
    return v;
}
