struct T {
    int pad;
    int x;
    int y;
};

struct S {
    char pad[4];
    struct T __far *t;
};

void __far __pascal upd(struct S __far *s, int x, int y)
{
    if (s) {
        if (x != -1)
            s->t->x = x;
        if (y != -1)
            s->t->y = y;
    }
}
