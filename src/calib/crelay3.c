/* Round-2 relay harvest (batch 1): framed far-Pascal wrappers around one far
 * call. Every object call site is `9A ...`; the image has `90 0E E8 rel16`
 * because LINK /FARCALLTRANSLATION (/F + /PACKC) rewrote it (CONVENTIONS.md).
 *
 * The object is 286 bytes on purpose: that is the size at which MSC's compact
 * FIXUPP offsets wrap modulo 256, which `omfdump.unwrap_fixup_offsets` repairs.
 */
extern int __far __pascal sub2(int a, int b);
extern int __far __pascal sub1(int a);
extern int __far __fastcall fsub(int a);

/* two arguments relayed (18 B each) */
int __far __pascal F_1E16(int a, int b) { return sub2(a, b); }
int __far __pascal F_201B(int a, int b) { return sub2(a, b); }
int __far __pascal F_21BA(int a, int b) { return sub2(a, b); }
int __far __pascal F_2DF1(int a, int b) { return sub2(a, b); }
int __far __pascal F_3C04(int a, int b) { return sub2(a, b); }
int __far __pascal F_4692(int a, int b) { return sub2(a, b); }

/* (a, 1) (17 B each) */
int __far __pascal F_1DFC(int a) { return sub2(a, 1); }
int __far __pascal F_1E56(int a) { return sub2(a, 1); }
int __far __pascal F_4DAF(int a) { return sub2(a, 1); }

/* one argument relayed (15 B each) */
int __far __pascal F_2214(int a) { return sub1(a); }
int __far __pascal F_349A(int a) { return sub1(a); }
int __far __pascal F_37A6(int a) { return sub1(a); }

/* call result multiplied by the second argument (18 B) */
int __far __pascal F_3895(int a, int b) { return sub1(a) * b; }

/* constant forwarded in AX to a far fastcall, result returned (9 B) */
int __far F_418C(void) { return fsub(0x1A); }

/* call for its side effect, then return -3 (12 B) */
int __far F_3390(void) { fsub(0x26); return -3; }
