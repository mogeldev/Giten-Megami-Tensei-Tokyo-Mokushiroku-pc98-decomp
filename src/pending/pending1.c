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
