/* Two single-form functions (round 20):
     20b2:0000 (14 B, __far __pascal, 1 int param):
         mov ax,[bp+6]; or [0x6DE],ax; leave; retf 2
         -> void: g_or |= x;   (the original stores back into the global!)
     20ab:000c (20 B, __far, spin wait with reload in the loop body):
         ENTER 2; ax=[0x6DA] -> [bp-2]; L: ax=[0x6DA]; cmp [bp-2],ax;
         je L; leave; retf
         -> s = g_watch; while (g_watch == s);
   (inventory size 18 at 20b2:0000 runs into the following getter
    'mov ax,[g]; retf' — match with --size 14.) */
int g_or;
volatile int g_watch;      /* interrupt/timer flag: MSC must not hoist the load */

void __far __pascal or_join(int x)
{
    g_or |= x;
}

void __far wait_change(void)
{
    int s;

    s = g_watch;
    while (g_watch == s)
        ;
}
