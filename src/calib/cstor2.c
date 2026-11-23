/* Multi-store forms (round 55).

   4e8e:0008 (37 B, near pascal retn 10 = five word arguments):
     8B 46 0C / A3 02 2D    g_2d02 = a   (first declared is at bp+0xC)
     8B 46 0A / A3 04 2D    g_2d04 = b
     8B 46 08 / A3 06 2D    g_2d06 = c
     8B 46 06 / A3 08 2D    g_2d08 = d
     8B 46 04 / A3 0A 2D    g_2d0a = e   (last declared is at bp+4)
   -> source order equals store order, as with STORE4.

   2aa3:0048 (38 B, far pascal retf 4):
     xor ax,ax
     les bx / mov bx,[bp+6]; mov es,[bp+8]
     then zero six words of the struct in the order +6, +0, +8, +2, +0xA, +4.
   -> the scattered order is what the source asks for, so the stores are written
      in exactly that sequence.
*/
int g_2d02;
int g_2d04;
int g_2d06;
int g_2d08;
int g_2d0a;

struct Z {
    int a, b, c, d, e, f;
};

void __near __pascal store5(int a, int b, int c, int d, int e)
{
    g_2d02 = a;
    g_2d04 = b;
    g_2d06 = c;
    g_2d08 = d;
    g_2d0a = e;
}

void __far __pascal zero_z(struct Z __far *p)
{
    p->d = 0;
    p->a = 0;
    p->e = 0;
    p->b = 0;
    p->f = 0;
    p->c = 0;
}
