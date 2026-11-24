struct S{int id; char pad[28];}; extern struct S __far g_tab[]; extern int g_n; int __far __pascal F_379E(int id){ int r=-1; int i; for(i=0;i<g_n;i++) if(g_tab[i].id==id) r=i; return r; }
