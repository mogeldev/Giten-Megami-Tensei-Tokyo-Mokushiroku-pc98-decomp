/* Slot-Fuellroutine — Original 458e:a20e (166 B, __far __pascal, 1 Far-Param).
   Byte-abgeleitete Form:
     - slots als char-Array (Slotgroesse 0x27=39 ist UNGERADE — MSC rundet
       Strukturen auf gerade, daher kein struct im Original)
     - p = i*0x27 als lokale Temperatur -> lebt in [bp-2] (Original: 89 46 fe)
     - Feldoffs als konstante disp16 (0,2,4,9,11,13,15,19) wie im Original
     - if (i >= 0) -> or/jge; src unsigned -> sub ah,ah-Extends
   Externe Helfer sind Standins; Near-Call-Ziele sind Relocations. */
extern int  __near get_slot(void);       /* Original 4fab:000a  */
extern int  __near conv(int c);          /* Original 458e:a1f6 */
extern void __near slot_update(void);    /* Original 458e:a1ea */

unsigned char slots[16 * 0x27];

void __far __pascal slot_fill(unsigned char __far *src)
{
    unsigned char __far *p;
    int q;
    int i;

    i = get_slot();
    if (i >= 0) {
        q = i * 0x27;
        p = src;
        *(int __near *)&slots[q + 0]  = *p++;
        *(int __near *)&slots[q + 2]  = *p++;
        *(int __near *)&slots[q + 4]  = conv(*p++);
        *(int __near *)&slots[q + 9]  = *p++;
        *(int __near *)&slots[q + 11] = *p++;
        *(int __near *)&slots[q + 13] = *p++;
        *(int __near *)&slots[q + 15] = *p++;
        *(int __near *)&slots[q + 19] = *p++;
        slot_update();
    }
}
