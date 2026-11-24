/* Round-85 harvest: five pure relays found by screening for units whose body is
 * nothing but pushes, calls and a return. Each needed exactly one lever - a register
 * parameter, a fastcall tail, or the right unit size (the inventory includes a
 * padding byte in several of them). */
extern int __far __pascal h(int a, int b, int c);
extern int __far __pascal h0(void);
extern int __far __pascal h1(int a);
extern int __far __pascal h2(int a);
extern int __far __fastcall h2f(int a);
extern int __far __pascal h3(int a, int b, int c);
extern int __far __pascal h4(int a, int b, int c);
extern int __far __pascal h1b(int a, int b);

void __far __pascal F_47C0(register int a) { h(a, 1, 0x64); }
void __far __pascal F_4AA1(int a) { h2(h1(a)); }
void __far __pascal F_2D3E(int a, int b) { h2f(h1b(a, b)); }
void __far __pascal F_2D58(int a) { h3(h0(), a, 1); }
void __far __pascal F_2E7A(int a, int b) { h2(h4(h0(), a, b)); }
