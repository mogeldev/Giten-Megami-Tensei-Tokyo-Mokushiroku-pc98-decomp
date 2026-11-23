/* Value classifier, original 1e14:0008 (32 B, MATCH, per-file /Ox /Oa /Os):
     8B 56 06 / 0B D2 / 75 04    if (v == 0) ...
     33 C0 / EB 0E               return 0
     81 FA FF 00 / 76 05         v > 0xFF -> 2 else 1
     B8 02 00 / EB 03 / B8 01 00
   The value is staged in DX (`8B 56 06 / 0B D2`) and the compare is unsigned
   (`76` = jbe). */
int __far __pascal kind_of(unsigned v)
{
    if (v == 0)
        return 0;
    return (v > 0xFF) ? 2 : 1;
}
