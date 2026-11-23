unsigned char g_995b;
unsigned char g_995c;
int g_9954;
int g_9956;
int g_9958;

extern void __near __pascal HELP5(int, unsigned char, int, int, int);
extern void __near __pascal HELP6(int, unsigned char, int, int, int, int);

void __far relay_globals5(void)
{
    HELP5(g_995b, g_995c, g_9954, g_9956, g_9958);
}

void __far __pascal relay_globals(int a)
{
    HELP6(g_995b, g_995c, g_9954, g_9956, g_9958, a);
}
