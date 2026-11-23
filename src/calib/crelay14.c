/* Round-5: /Ot (speed) is needed for the rotated while-loop: the test is
 * placed first, the body starts with one alignment `90`, and the translated
 * call follows it. /Os places no padding here. */
extern int __far __pascal sub0(void);

int __far __pascal F_20AD(int n)
{
    while (n) {
        sub0();
        n--;
    }
}
