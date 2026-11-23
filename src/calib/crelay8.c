/* Round-3 harvest, /Os group: small wrappers whose far calls are LINK /F
 * translations in the image (object side: `9A`). See CONVENTIONS.md. */
extern int g_1bf0, g_06e4;
extern char g_23d0[], g_23d8[], g_2426[], g_2436[], g_2448[], g_246c[];
extern int __far __pascal sub0(void);
extern int __far __pascal sub1(int a);
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal sub3(int a, int b, char __far *p);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);
extern char __far __pascal bsub(void);
extern int __far __pascal suba(void);
extern int __near __pascal nsub1(int a);

int __far F_330D(void) { return h1(sub0()); }

int __far F_2D91(void)
{
    int t;
    suba();
    t = bsub();
    g_1bf0 = t;
    return t;
}

void __far F_20B3(void) { suba(); sub0(); g_06e4 = 1; }

int __far __pascal F_218A(int a) { nsub1(-1); return sub1(a); }

int __far __pascal F_39F8(int a, int b) { return b - sub1(a); }

int __far __pascal F_31D3(int a) { return h2(sub1(a)); }
int __far __pascal F_31F6(int a) { return h2(sub1(a)); }
int __far __pascal F_34B7(int a) { return h2(sub1(a)); }

int __far __pascal F_4E86(int a, int b, int c) { return sub2(b, c) - a; }

int __far __pascal F_47C1(int a, int b, int c) { return sub1(c + b + a); }

int __far __pascal F_4956(int a, int b) { return sub3(a, b, g_23d0); }
int __far __pascal F_4961(int a, int b) { return sub3(a, b, g_23d8); }
int __far __pascal F_4965(int a, int b) { return sub3(a, b, g_2426); }
int __far __pascal F_4967(int a, int b) { return sub3(a, b, g_2436); }
int __far __pascal F_4968(int a, int b) { return sub3(a, b, g_2448); }
int __far __pascal F_4969(int a, int b) { return sub3(a, b, g_246c); }
