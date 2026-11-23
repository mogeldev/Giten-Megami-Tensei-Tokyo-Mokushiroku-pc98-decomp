/* Slot fill routine — original 458e:a20e (166 B, __far __pascal, 1 far param).
   Byte-derived form:
     - slots as a char array (slot size 0x27 = 39 is ODD — MSC rounds structs
       to even, so the original cannot have used a struct)
     - q = i*0x27 as a local temporary -> lives in [bp-2] (original: 89 46 fe)
     - field offsets as constant disp16 (0,2,4,9,11,13,15,19) like the original
     - if (i >= 0) -> or/jge; src unsigned -> sub ah,ah extends
   External helpers are stand-ins; their near call targets are relocations. */
extern int  __near get_slot(void);       /* original 4fab:000a  */
extern int  __near conv(int c);          /* original 458e:a1f6 */
extern void __near slot_update(void);    /* original 458e:a1ea */

unsigned char slots[16 * 0x27];

void __far __pascal slot_fill(unsigned char __far *src)
{
    int q;
    int i;

    i = get_slot();
    if (i >= 0) {
        q = i * 0x27;
        *(int __near *)&slots[q + 0]  = *src++;
        *(int __near *)&slots[q + 2]  = *src++;
        *(int __near *)&slots[q + 4]  = conv(*src++);
        *(int __near *)&slots[q + 9]  = *src++;
        *(int __near *)&slots[q + 11] = *src++;
        *(int __near *)&slots[q + 13] = *src++;
        *(int __near *)&slots[q + 15] = *src++;
        *(int __near *)&slots[q + 19] = *src++;
        slot_update();
    }
}
