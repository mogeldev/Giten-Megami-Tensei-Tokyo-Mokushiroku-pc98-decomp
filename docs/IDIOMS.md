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

## MSC 7.0 /Os — beobachtete Idiome (Kalibrierung 2026-11-23)
- `return g;` (Leaf, /Gs): nackte Form `A1 <disp> CB` — kein ENTER, keine Register-
  saves. Gleiches gilt für 32-Bit (`A1` + `8B 16`) und Near-Varianten (`C3`).
- `g |= 0x40;`: direktes `80 0E <disp> 40`.
- `if (g < K) g++;`: `83 3E <disp> K / 7D 04 / FF 06 <disp> / C3` (jge skippt Body).
- **Ternär-Falle**: `return (g < K) ? g : -1;` kompiliert MSC7-/Os zur
  Early-Return-Form (zwei RET) — NICHT zur Sprung-Merge-Form des Originals
  (4fab:000a: `jl / mov ax,-1 / jmp / mov ax,[g] / ret`). Lokale Ergebnisvariable
  erzwingt stattdessen ENTER+Stackslot. Offen: welche Quellform die Merge-Form
  erzeugt (Kandidat: Ausdruck mit Nachnutzung des Werts — prüfen, wenn Kontext
  der Aufrufstelle bekannt ist).
