/* Round-9 harvest: more framed + translated-call combinations. Note the
 * compiler bug found while transcribing `388d:0006`: MSC 7 aborts silently
 * (no object, no log) on `sub3(sub2(a, a), 0)` - a nested call followed by a
 * zero constant argument - so that unit stays open. */
extern int __far __pascal l0(void);
extern int __far __pascal l1(int a);
extern int __far __pascal l2(int a, int b);
extern int __far __pascal l3(int a);
extern int __far __pascal sub0(void);
extern int __far __pascal sub3(int a, int b, int c);
extern int __far __pascal h(int a);
extern int __far __pascal h2(int a);

int __far __pascal F_38B7(register int a) { l1(a); return l3(a); }
int __far __pascal F_3A18(register int a) { l1(a); return l3(a); }
int __far __pascal F_4A41(register int a) { return h(l1(a)); }
int __far __pascal F_4E72_22(int a, int b) { return sub3(sub0(), a, b); }
int __far __pascal F_3A6F(register int a) { l1(a); return l2(a, 1); }
int __far __pascal F_31CF_26(register int a) { h(l1(a)); return l3(a); }
int __far __pascal F_31D3_56(register int a) { h(l1(a)); return l3(a); }
int __far __pascal F_31F6_48(register int a) { l1(a); l0(); return h2(a); }

/* keeps the last symbol sliceable */
int __far F_TAIL9(int x) { return x; }
