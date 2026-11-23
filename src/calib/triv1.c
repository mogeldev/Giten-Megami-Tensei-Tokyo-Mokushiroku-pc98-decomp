/* Kalibrier-Quelldatei (Phase 0): triviale Getter/Setter/Leaf-Funktionen.
   Dient nur dem Toolchain-Nachweis: kompiliert mit MSC 7.0 (/Gx + Memory-Modell),
   Objekt wird spaeter gegen echte DDS98-Funktionen bytewise verglichen. */
int g_val = 0;

int get_val(void)
{
    return g_val;
}

void set_val(int v)
{
    g_val = v;
}

int add2(int a, int b)
{
    return a + b;
}
