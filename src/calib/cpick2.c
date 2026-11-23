char __far *g_pa;
char __far *g_pb;

char __far *__far __pascal pick_flag(int flag)
{
    if (flag == 0)
        return g_pa;
    return g_pb;
}