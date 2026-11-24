struct P{int a;int b;}; extern struct P g; struct P __far __pascal F_477B(void){ struct P t; t.a=g.a; t.b=g.b; return t; }
