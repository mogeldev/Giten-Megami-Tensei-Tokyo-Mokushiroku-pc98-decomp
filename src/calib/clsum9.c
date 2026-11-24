struct R{char pad[0x1a2]; int a0:11; unsigned r0:5; int x0; int a1:11; unsigned r1:5; int x1; int a2:11; unsigned r2:5; int x2; int a3:11; unsigned r3:5; int x3; int a4:11; unsigned r4:5; int x4; int a5:11; unsigned r5:5; int x5; int a6:11; unsigned r6:5; int x6; int a7:11; unsigned r7:5; int x7;};
int __near __pascal G(int);
int __far __pascal F_444A(struct R __far *p, int m){ int t; t=0; if(m&1){ t=G(p->a0); t+=G(p->a1); t+=G(p->a2); t+=G(p->a3); t+=G(p->a4); } if(m&2){ t+=G(p->a5); t+=G(p->a6); t+=G(p->a7); } return t; }
