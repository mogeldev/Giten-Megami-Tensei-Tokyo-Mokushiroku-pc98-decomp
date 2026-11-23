/* Far-call relays whose image bytes are Microsoft LINK /FARCALLTRANSLATION
 * (/F with /PACKC) output: the compiler emits `9A seg off` for an external far
 * callee, and the linker rewrites it to `90 0E E8 rel16` (NOP; PUSH CS; CALL
 * NEAR) because the callee ends up in the caller's physical segment.
 * match.py recognises exactly that rewrite and masks the 5-byte slot; the
 * rel16 is link-layout dependent, like every other relocated operand. */
extern int g_78c8, g_78ca, g_78cc, g_78c4;
extern int __far __fastcall fsub(int);
extern int __far __pascal psub(int);
extern int __far fnone(void);

int __far F_3DCD_A(void) { return fsub(g_78c8 + 1); }
int __far F_3DCD_14(void) { return fsub(g_78c8 - 1); }
int __far F_3DCF_E(void) { return fsub(g_78ca + 1); }
int __far F_3DCF_18(void) { return fsub(g_78ca - 1); }
int __far F_3DD1_C(void) { return fsub(g_78cc + 1); }
int __far F_3DD1_16(void) { return fsub(g_78cc - 1); }

int __far F_3EA8(void) { return psub(14); }
int __far F_3EA9(void) { return psub(0); }

int __far F_2E68(void) { return fnone(); }
int __far F_3BD6(void) { return fnone(); }
int __far F_3DD5(void) { return fnone(); }
int __far F_3E3F(void) { return fnone(); }

int __near F_3D94(void) { return psub(g_78c4); }
