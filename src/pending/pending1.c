/* Sources for ledger rows that are PENDING: the C is believed correct, and each one is a
 * byte or two from matching. Keeping them compiled in one file lets `tools/recheck.py`
 * test every pending hypothesis in exchange for a single compile, so if a flag, a compiler
 * or an idea turns up, the whole set is re-tested at once instead of one round per unit.
 *
 * Register the source/symbol/flags for each in `tools/pending.txt`. */

/* 2a28:0000 - the clamp pair. Original wants the working value in DX; MSC uses AX. */
int __far __pascal P_2A28(int a, int b, int c) { if (b <= a) { if (c < a) a = c; } return a; }
unsigned __far __pascal P_2A29(unsigned a, unsigned b, unsigned c) { if (b <= a) { if (c < a) a = c; } return a; }

/* 20b4:0130 - saved value pushed from AX rather than from the frame slot. */
extern int __far __cdecl q1(void);
extern void __far __cdecl q2(void);
extern void __far __cdecl q3(int r);
void __cdecl P_20B4(void) { int r; r = q1(); q2(); q3(r); }

/* 3ebd:0068 - far deref of a call result; MSC loads ES before BX, the original the reverse. */
extern int __far * __far __pascal q4(int a);
extern int g_29c0;
int __near __cdecl P_3EBD(void) { return *q4(g_29c0); }

/* 20f6:0000 - fastcall; MSC tests with `test`, the original with `and`. */
extern void __far __pascal q5(void);
void __fastcall P_20F6(unsigned x) { if (x & 1) q5(); if (x & 2) q5(); }

/* 2603:463c - `|` operand order; MSC always puts the array load first. */
extern char g_4642[];
extern char g_76b4[];
char __far __pascal P_2603(int n) { return g_4642[n & 7] | g_76b4[n / 8]; }

/* 4962:000c - a table scan ending in the padded-jump shape (`EB 03 90`). */
extern int g_f623[];
int __far __pascal P_4962(int a)
{
    int i;
    for (i = 0; g_f623[i] != -1; i++) { if (g_f623[i] == a) return 1; }
    return 0;
}

/* 4aae:0006 - early return plus a padded `EB 07 90`. */
extern int __far __pascal q6(int a);
int __far __pascal P_4AAE(int a) { if (a == -1) return a; return q6(a); }

/* 3d91:0020 - a global comparison whose two return paths are joined differently. */
extern int g_1b12, g_1b14;
int __near __cdecl P_3D91(void) { return g_1b12 < g_1b14; }

/* 31df:0004 - a two-case switch the original walks with inc/dec. */
extern void __far __pascal q7(int x);
extern void __far __pascal q8(int x);
void __far __pascal P_31DF(int v, int sel)
{
    switch (sel) {
    case 0: q7(v); break;
    case 1: q7(v); q8(v); break;
    }
}

/* 2e68:000c - a two-word signed comparison; one branch distance. */
int __far __pascal P_2E68(long x, long y)
{
    if (x < y) return -1;
    if (x > y) return 1;
    return 0;
}

/* 41d8:000c - a far pointer subscript; the index is scaled with add instead of shl. */
extern int __far * __far __pascal q9(int x);
extern int g_2f5c;
int __far __pascal P_41D8(int i) { int __far *p; p = q9(g_2f5c); return p[i]; }

/* 1ab4:0028 - the second function of a mis-cut window; DX-cached state word. */
extern int g_536e;
extern long g_9950, g_9b18, g_9b10;
extern void __far __pascal q10(int x);
extern void __far __pascal q11(char __far *a, char __far *b, char __far *c);
void __near __cdecl P_1AB4B(void)
{
    if (g_536e != 0 && g_536e != -1) q10(g_536e);
    g_536e = 0;
    q11((char __far *)&g_9950, (char __far *)&g_9b18, (char __far *)&g_9b10);
}

/* 3b5d:0006 - the second function of a split window; one pad byte after a far-pointer push. */
extern int g_995d;
extern void __far __pascal q12(char __far *p);
void __near __cdecl P_3B5D(void) { if (!g_995d) q12((char __far *)0x1766); }
