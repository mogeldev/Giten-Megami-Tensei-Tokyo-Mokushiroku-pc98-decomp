extern int __far __pascal target_22fc(int, int);
extern int __far __pascal target_92bc(int);
extern int __far __pascal target_92e4(int);
extern int __far __pascal target_9326(int);
extern int __far __pascal target_26de(int);
extern int __far __pascal target_27b8(int);
extern int __far __pascal target_27fe(int);
extern int __far __pascal target_ae58(int, int);
extern int __far __pascal target_474a(int, int, int);

int __far __pascal relay_22fc(int a, int b) { return target_22fc(a, b); }
int __near __pascal relay_92bc(int a) { return target_92bc(a); }
int __near __pascal relay_92e4(int a) { return target_92e4(a); }
int __near __pascal relay_9326(int a) { return target_9326(a); }
int __far __pascal relay_26de(int a) { return target_26de(a); }
int __far __pascal relay_27b8(int a) { return target_27b8(a); }
int __far __pascal relay_27fe(int a) { return target_27fe(a); }
int __far __pascal relay_ae58(int a, int b) { return target_ae58(a, b); }
int __far __pascal relay_474a(int a, int b, int c) { return target_474a(a, b, c); }
