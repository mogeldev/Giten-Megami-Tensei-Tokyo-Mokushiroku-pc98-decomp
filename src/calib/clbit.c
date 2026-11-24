struct B{unsigned a:5; unsigned b:1; unsigned c:1; unsigned d:9;}; extern struct B __far g;
void __far __pascal F_2D7D(unsigned v){ g.c=1-v; g.b=v; }
