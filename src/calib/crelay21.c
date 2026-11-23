/* Round-10 harvest: nested-expression call combinations. The call order is what
 * distinguishes these - MSC evaluates Pascal arguments left to right, so a
 * shape that evaluates the *inner* call first before pushing an argument
 * (`31dd:0008`) cannot be reproduced and stays open. */
extern int __far __pascal c0(void);
extern int __far __pascal c3(int a);
extern int __far __pascal d3(int a, int b, int c);
extern int __far __pascal l2(int a, int b);
extern int __far __pascal l3(long v);

int __far __pascal F_2D49_16(int a) { return d3(c3(1, 100, 0), a, 0); }
int __far __pascal F_31CF_08(int a) { return l3((long)l2(c0(), a)); }
