/* Round-18 harvest: two minimal units and a global store before a call. */
extern char g_0004;
extern int g_234a, g_9b40;
extern int __far __pascal fsub(int a);

/* an empty far function is exactly one byte (`CB`) */
void __far F_1270_C(void) { }

/* a byte global read compiles to the moffs form `A0 <disp>` then `cbw`; the
 * near return matters (`__far` would emit `CB`) */
int __near F_1534G(void) { return g_0004; }

/* an immediate store, then a global pushed into a far call */
void __far F_48D6(void)
{
    g_234a = -1;
    fsub(g_9b40);
}
