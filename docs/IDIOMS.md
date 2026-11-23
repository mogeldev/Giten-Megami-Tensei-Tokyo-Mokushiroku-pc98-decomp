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

## MSC 7.0 /Os — Slot-Routine 458e:a20e (Runde 17, 4 Hypothesen)
- Bestes C-Ergebnis 162/166 B (v3: `*src++`-Wanderung): ENTER, or/jge,
  `e9`-Branch (>127 Distanz erzwingt jge+3/jmp-rel16 von selbst),
  `imul ax,ax,0x27`, Stores als `[bx+disp16]` mit Feldoffs — alles passt.
- Offen: Original wandert den Offset NUR in si (nie Rueckschreiben); MSC7-C
  schreibt bei `*src++` den Parameter zurueck ([bp+6]/[bp+8]-Stores), bei einer
  lokalen Far-Pointer-Kopie gibt es dem Pointer ein Stack-Heim (ENTER 16,
  LES-hantieren). Verdacht: Quellform mit getrennten Segment/Offset-Zutritten
  (FP_SEG/FP_OFF-Stil) oder Inline-ASM.
- Ungerade Feld-/Slotgroessen (0x27=39): MSC7 rundet Strukturen auf — das
  Original nutzt folglich char-Array + Index-Arithmetik, keine Struktur.
- `__pascal` versaliert Symbolnamen (SLOT_FILL) und raeumt per `retf imm16`
  auf — wahre Aritaet am RET ablesbar (hier: 4 = ein Far-Pointer; Ghidras
  'param_2' war ein Konventionsartefakt).

## Slot-Subsystem: vermutlich Hand-ASM (Runde 17/18, Muster-These)
Vier Funktionen (4fab:000a Allokator, 4fac:000a Inkrement, 4fad:0006 conv,
458e:a20e Fueller) teilen Codegen-Idiome, die MSC7-/Os aus C nicht erzeugt:
- Sprung-Merge-Ternarform statt Early-Return (4fab)
- Register-Wanderung ohne Param-Rueckschreibung (458e:a20e)
- `add bx,bx` statt kanonischem `shl bx,1` (4fad:0006) — /Od//O1//O2 nutzen
  die SPEICHERform `add bx,[bp+4]`, nie die Registerform
Schlussfolgerung bis zum Gegenbeweis: dieses Subsystem wurde von den
Entwicklern per Assembler/Inline-ASM gebaut — fuer RELOCS-Verifikation bleibt
dort nur Umschreibung als __asm (Vorlagen-konform dokumentiert) oder PENDING.
Positive Nebenfaelle: /Os komprimiert Leaf-Frames (ENTER 0,0 -> push bp/mov
bp,sp, LEAVE bleibt) — das frame matcht das Original exakt.
