struct R{int a,b,c,d;}; extern struct R g_cur; extern struct R g_tab[32]; extern int g_n;
void __far __pascal F_3DB8(void){ struct R __far *p; if(g_n<32){ p=&g_tab[g_n]; g_n++; *p=g_cur; } }
