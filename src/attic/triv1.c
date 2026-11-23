/* Calibration source file (phase 0): trivial getters/setters/leaf functions.
   Serves only the toolchain proof: compiles with MSC 7.0 (/Gx + memory model),
   the object is later compared bytewise against real DDS98 functions. */
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
