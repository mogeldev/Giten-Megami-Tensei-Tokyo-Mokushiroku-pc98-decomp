# IDIOMS — je Toolchain getrennt

Regel 4a der Vorlage gilt universell und wird hier nicht wiederholt.
Nach jeder gelösten Diff-Ursache kommt genau die gefundene Regel hierher.

## MS C 8.x / x86-16 Real Mode — **kalibriert: NEIN**

Noch ungeprüfte Kandidaten (erst nach Kalibrierung als Regel vermerken):
- near vs far: cdecl-artige Stackrahmen (`BP`-basiert); MS-Schalter `/Gc` (pascal) möglich.
- Globals liegen in DGROUP (`DS`), Startup setzt `DS=0x58FC ≠ CS` → kein tiny/small.
- Registerwahl über Quelltextform gilt unverändert (Extra-Locals statt Inline-Casts).
- vorzeichen/Typbreite entscheiden die Instruktion (`jg/jl` vs `ja/jb`, `movzx`-Äquivalente).
- Set-Membership: OR-Kette vs `switch` (16-Bit-Compiler bauen oft lineare Vergleichsketten).
