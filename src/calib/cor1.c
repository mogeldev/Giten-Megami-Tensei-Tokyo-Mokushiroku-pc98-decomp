/* Zwei Einform-Funktionen (Runde 20):
     20b2:0000 (14 B, __far __pascal, 1 int-Param):
         mov ax,[bp+6]; or [0x6DE],ax; leave; retf 2
         -> void: g_or |= x;   (Original schreibt in die Globale zurueck!)
     20ab:000c (20 B, __far, Spin-Wait mit Reload im Schleifenkoerper):
         ENTER 2; ax=[0x6DA] -> [bp-2]; L: ax=[0x6DA]; cmp [bp-2],ax;
         je L; leave; retf
         -> s = g_watch; while (g_watch == s);
   (Inventargroesse 18 bei 20b2:0000 laeuft in den Folge-Getter
    'mov ax,[g]; retf' — match mit --size 14.) */
int g_or;
volatile int g_watch;      /* Interrupt-/Timer-Flag: MSC darf den Load nicht hochziehen */

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
