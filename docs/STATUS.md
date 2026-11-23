# STATUS

Zahlen aus dem Ledger (`docs/MATCHING.md`) und `tools/coverage.py` — Stand 2026-11-23,
Runde 20. Nicht aus dem Gedächtnis: vor jeder Aussage `tools/verify.py` laufen lassen.

## Ledger

| Status | Anzahl |
|---|---|
| MATCH | 0 |
| RELOCS | **14** |
| PENDING | **3** |

PENDING mit dokumentierter Ursache (Details in `docs/MATCHING.md`, Idiome in `docs/IDIOMS.md`):
1. `4fab:000a` — Slot-Index-Allokator, Sprung-Merge-Form (Hand-ASM-Verdacht)
2. `458e:a20e` — Slotfüllroutine, 162/166 B erreicht (Register-Wanderung ohne Stack-Rückschreibung)
3. `4fad:0006` — conv-Lookup, 14/16 B erreicht (`add bx,bx` vs. kanonisches `shl`)

## Coverage (ehrliche Byte-Metrik)

| Kategorie | Bytes |
|---|---|
| inventarisiert (1 970 Funktionen) | 306 814 |
| − Fremd-CRT (35 Signatur-Treffer) | 963 |
| − Daten/Fehlinventarisierung (`not_code.csv`) | 12 211 |
| = **Eigencode** | **293 640** |
| davon **verifiziert** | **100 (0,034 %)** |
| PENDING-Bytes | 198 |

Die Fehlinventarisierung ist belegt: CD-3F-Soundtreiber-Befehlsblöcke (NMUSE/MIDE,
6-Byte-Stride), lineare Wort-Tabellen, ein 10,9-KB-Nullfeld, ein ASCII-String.
Bereinigung dieser Einträge im Inventar steht noch aus.

## Toolchain

- **MSC 7.0 (CL 8.00, 1992)** läuft: dosbox-x + HDPMI32-TSR, `-nopromptfolder`,
  APPDATA-Redirect, `cycles=max` — Rezept in `docs/CONVENTIONS.md`.
- CFLAGS **bestätigt: `/G1 /AM /Gs /Os`** (durch byte-identische Kalibrierfunktionen).
- `build.py` kompiliert reproduzierbar; `omfdump.py` liest MSC-OMF inkl. der
  kompakten 0x9C-Fixups; `match.py` maskiert Linker-Operanden aus dem Objekt.

## Offen (Reihenfolge für die nächsten Runden)

1. Inventar bereinigen: `not_code.csv` aus `functions.csv` ausschließen
   (macht Nenner und Funktionszahl ehrlich)
2. `LINK.EXE` (DOSX16) hängt unter dosbox-x in allen DPMI-Varianten — Voraussetzung
   für `build_replacement` (Phase 6); Kandidat: nativer OMF-Linker (jwlink)
3. Slot-Subsystem: `__asm`-Rekonstruktion erwägen (dort ist C nachweislich erschöpft)
4. Weiter im Familien-Workflow: ALU-/DOS-Helfer mit `55 8b ec`-Rahmen
