/* Round-8 harvest: the framed + translated-call family (219 units, 10.9 KB with
 * no blocking trait). Every function here is a two-call combination whose far
 * call sites are LINK /F translations in the image (object side: `9A`). */
extern int __far __pascal sub0(void);
extern int __far __pascal sub1(int a);
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal sub3(int a, int b, int c);
extern int __far __pascal h1(int a);
extern int __near __pascal nret2(int a, int b);
extern long __far __pascal lsub1(int a);
extern long __far __pascal lsub3(int a, int b, int c);
extern int __far __pascal isub2(long v);

/* a long returned by one call, forwarded to the next (`52 50` = push dx; push ax) */
int __far __pascal F_372A(int a) { return isub2(lsub1(a)); }
int __far __pascal F_372F(int a) { return isub2(lsub1(a)); }
int __far __pascal F_4727(int a) { return isub2(lsub1(a)); }
int __far __pascal F_4A95(int a) { return isub2(lsub1(a)); }
int __far __pascal F_4AA2(int a) { return isub2(lsub1(a)); }
int __far __pascal F_4AB1(int a) { return isub2(lsub1(a)); }

int __far __pascal F_473F(int a, int b, int c) { return isub2(lsub3(a, b, c)); }

/* call result forwarded through `push ax` */
int __far __pascal F_3A57(int a, int b) { return h1(sub2(a, b)); }
int __far __pascal F_49F2(int a, int b) { return h1(sub2(a, b)); }

/* leading no-argument call, then the real call */
int __far __pascal F_2D52(int a) { return sub3(sub0(), a, 0); }
int __far __pascal F_2E55(int a, int b) { sub0(); return sub2(a, b); }

/* far call result feeds a near-Pascal callee (the near call has no /F form) */
int __far __pascal F_3A58(int a, int b, int c) { return nret2(sub2(a, b), c); }

/* keeps the last symbol sliceable */
int __far F_TAIL5(int x) { return x; }
