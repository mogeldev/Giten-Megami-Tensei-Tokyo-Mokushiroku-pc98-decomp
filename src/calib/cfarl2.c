/* Second batch of LINK /F-translated relay units (see cfarl.c): every object
 * call site is `9A ...`; /FARCALLTRANSLATION rewrote it to `90 0E E8 rel16`
 * in the image once /PACKC had put the callee into this physical segment.
 *
 * `F_TAIL` is only a layout filler so that the symbol table slice of the last
 * claimed function does not end exactly at the end of the LEDATA record; it is
 * not a recovered function. */
extern int g_192c, g_78c4, g_1cee, g_1cec, g_9954, g_9956;
extern char g_17d2[];
extern int __far __pascal none(void);
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal sub3(char __far *p, int a, int b);
extern int __far __pascal h(int a);

void __far F_3BD6_C(void) { if (g_192c == 0) none(); }
int __near F_3D94_2(void) { return g_78c4 = sub2(5, 2); }
int __far F_322B(void) { return sub2(g_1cee, g_1cec); }
int __far F_4E6D(void) { return sub2(g_9954, g_9956); }
int __far F_3BAA(void) { return sub3(g_17d2, 0, 0); }
int __far F_3309(void) { return h(none()); }

int __far F_TAIL(void) { return 0; }
