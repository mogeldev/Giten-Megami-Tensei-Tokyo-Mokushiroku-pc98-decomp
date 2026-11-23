extern char g_468c[], g_7d8e[], g_79ce[], g_860e[], g_3970[];
extern int g_3ab6, g_3ab4, g_2f52;
extern int __far __pascal f0c7e(char __far *, int, int);
extern int __far __pascal f7aa8(int, int);
extern int __far __pascal f0cd2(int, int, char __far *);
extern int __far __pascal f161e(int, char __far *);
extern int __far __pascal f9326(int);
extern int __far __pascal f62f8(int, int, int, int);
extern int __far __pascal f91c4(int, int);
extern int __far __pascal f4718(char __far *, int);
extern int __far __pascal f4f64(char __far *, int, int);

int __far __pascal relay_0c7e(int a, int b) { return f0c7e(g_468c, a, b); }
int __near relay_7aa8_10(void) { return f7aa8(1, 10); }
int __far __pascal relay_0cd2(int a, int b) { return f0cd2(a, b, g_7d8e); }
int __far __pascal relay_161e(int a) { return f161e(a, g_79ce); }
int __far relay_7aa8_70(void) { return f7aa8(1, 70); }
int __far relay_9326_global(void) { return f9326(g_2f52); }
int __far __pascal relay_62f8(int a, int b) { return f62f8(g_3ab6, g_3ab4, a, b); }
int __near relay_91c4(void) { return f91c4(0, 4096); }
int __far __pascal relay_4718(int a) { return f4718(g_860e, a); }
int __far relay_4f64(void) { return f4f64(g_3970, 0, 0); }

extern int g_1cd4, g_85f4;
extern int __far __pascal f01a4(int);
extern int __far f883e(void);
extern void __far __fastcall f8850(int);

void __far save_01a4(void) { g_1cd4 = f01a4(0); }
void __near save_883e(void) { g_85f4 = f883e(); }
void __near use_85f4(void) { f8850(g_85f4); }
