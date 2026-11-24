/* Round-40 harvest: a near-Pascal function that relays two DGROUP object
 * pointers plus an int, then returns one of the pointers (`B8 <disp>` + `8C DA`). */
extern char g_10d8[];
extern char g_6cf6[];
extern void __far __pascal h3(int x, char __far *a, char __far *b);

char __far * __near __pascal F_2183(int x)
{
    h3(x, g_10d8, g_6cf6);
    return g_6cf6;
}
