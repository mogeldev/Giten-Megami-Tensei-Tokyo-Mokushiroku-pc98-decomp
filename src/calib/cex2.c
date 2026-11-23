/* Three functions in one blob, original 458e:8642 (60 B merged in the inventory):

     A1 54 99 / A3 54 2C / A1 56 99 / A3 56 2C / CB            (12 B)
        -> g_2c54 = g_9954; g_2c56 = g_9956;   (state -> shadow)
    55 8B EC 8B 46 0A A3 54 2C 8B 46 08 A3 56 2C
             8B 46 06 A3 63 99 C9 CA 06 00                      (24 B)
        -> far pascal setter with three word arguments; pascal pushes left to
           right, so [bp+0xA] is the first declared and [bp+6] the last:
           g_2c54 = a; g_2c56 = b; g_9963 = c;
     A1 54 2C A3 54 99 A1 56 2C A3 56 99 A1 63 99 A3 58 99 CB   (20 B)
        -> g_9954 = g_2c54; g_9956 = g_2c56; g_9958 = g_9963;  (shadow -> state)
*/
int g_9954;
int g_9956;
int g_9958;
int g_9963;
int g_2c54;
int g_2c56;

void __far state_to_shadow(void)
{
    g_2c54 = g_9954;
    g_2c56 = g_9956;
}

void __far __pascal shadow_set(int a, int b, int c)
{
    g_2c54 = a;
    g_2c56 = b;
    g_9963 = c;
}

void __far shadow_to_state(void)
{
    g_9954 = g_2c54;
    g_9956 = g_2c56;
    g_9958 = g_9963;
}
