/* Round-76 harvest: a no-argument call followed by a call that forwards a far
 * pointer's field. */
struct S { char pad[6]; short f6; };
extern int __far __pascal h1(void);
extern int __far __pascal h2(int a);

void __far __pascal F_2B8B(struct S __far *p)
{
    h1();
    h2(p->f6);
}
