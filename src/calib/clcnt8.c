struct E{int k:11; unsigned r:5; int x;};
int __far __pascal F_32BD(int key,struct E __far *p){ int n=0; if(p[0].k==key) n++; if(p[1].k==key) n++; if(p[2].k==key) n++; if(p[3].k==key) n++; if(p[4].k==key) n++; if(p[5].k==key) n++; if(p[6].k==key) n++; if(p[7].k==key) n++; return n; }
