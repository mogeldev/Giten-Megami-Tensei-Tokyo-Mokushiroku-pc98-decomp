/* Round-2 relay harvest (batch 2).
 * `/Ox` is required for the fastcall reset: it stages the old value in DX
 * (`8B 16 <g>`), whereas /Os copies it through CX. The two boolean relays are
 * byte-identical under both levels.
 * Call sites are LINK /F-translated in the image (see CONVENTIONS.md). */
extern int __far __pascal sub0(void);
extern int g_78c8, g_78ca, g_78cc;

int __near F_3A89(void) { return sub0() != 0; }
int __near F_3A8A(void) { return sub0() != 0; }

int __far __fastcall F_3DCC(int v)
{
    int old = g_78c8;
    g_78c8 = v;
    g_78ca = 0;
    g_78cc = 0;
    return old;
}
