# STATUS

<!-- GENERIERT von tools/report.py am 2026-11-23 — Zahlen nicht von Hand -->
<!-- Handgeschriebener Teil zwischen MANUAL-BEGIN und MANUAL-END bleibt erhalten. -->

## Ledger (Quelle: docs/MATCHING.md)

| Status | Anzahl |
|---|---|
| MATCH | 0 |
| RELOCS | **14** |
| PENDING | **5** |

PENDING-Faelle (Details in `docs/MATCHING.md`, Idiome in `docs/IDIOMS.md`):

- `458e:a20e` **SLOT_FILL** (166 B) — Slotfuellroutine (pascal, 1 Far-Param, 8 Felder 0/2/4/9/11/13/15/19, conv+update-Calls). 4 Hypothesen: v3 (162/166 B!) fehlen nur die Stack-Rueckschre
- `4fad:0006` **CONV** (16 B) — Lookup table[c] (Wort-Tabelle DGROUP 0x396A, near-pascal). 5 Quellformen + /Od-/O1-/O2 getestet: /Os liefert ALLES identisch (55 8b ec-Rahmen, [bp+4],
- `4fab:000a` **get_39f8_clamped** (16 B) — Slot-Index-Allokator (Aufrufer FUN_458e_a20e: Sentinel -1, Slots 0x27 B). BESTE Variante jetzt **/Ox**: 14/16 B — `83 3E d 10 / 7C 05 / B8 FFFF` ident
- `1f2d:000e` **CLAMP_A** (20 B) — min(max(x,1),g), __fastcall (Arg in AX, nacktes retn), GLOBAL 0x4688. Original ohne Rahmen und mit DX-Temp (`8B 16 d / 3B C2 / 7E 02 / 8B C2`). MSC7 e
- `1f2f:0002` **CLAMP_B** (20 B) — identische Form, Global 0x468A — Geschwister von CLAMP_A, gleiche Ursache

## Coverage (ehrliche Byte-Metrik)

| Kategorie | Wert |
|---|---|
| Inventar-Einträge | **1956** Code-Funktionen + **14** Daten |
| Daten (belegt, `not_code.csv`) | 12211 B |
| Code-Bytes | 294603 |
| − Fremd-CRT (Signaturen) | 963 |
| = **Eigencode-Bytes** | **293640** |
| davon **verifiziert** | **100 (0.034%)** |
| PENDING-Bytes | 238 |

Code-Funktionen: **1956**, davon verifiziert **14**.

## Regionen (64 KiB)

| Region | Funktionen | ok | Code-B | verifiziert | CRT | Daten | PENDING |
|---|---|---|---|---|---|---|---|
| 0x0000 | 534 | 1 | 65244 | 4 (0.0%) | 897 | 360 | 40 |
| 0x0001 | 406 | 4 | 65783 | 48 (0.1%) | 0 | 569 | 0 |
| 0x0002 | 545 | 5 | 65692 | 24 (0.0%) | 0 | 0 | 0 |
| 0x0003 | 429 | 4 | 64548 | 24 (0.0%) | 0 | 0 | 198 |
| 0x0004 | 42 | 0 | 33336 | 0 (0.0%) | 66 | 11282 | 0 |

<!-- MANUAL-BEGIN -->
## Toolchain

- **MSC 7.0 (CL 8.00, 1992)**: dosbox-x + HDPMI32-TSR, `-nopromptfolder`,
  APPDATA-Redirect, `cycles=max` — Rezept in `docs/CONVENTIONS.md`.
- CFLAGS **bestaetigt: `/G1 /AM /Gs /Os`** (byte-identische Kalibrierfunktionen).
  ACHTUNG: `/Oy` bzw. `/Ox` entfernen den Rahmen — fuer rahmenlose Originale
  sind Flags **pro Quelldatei** zu waehlen (s. `docs/IDIOMS.md`, Runde 23).
- Werkzeuge: `build.py` (kompiliert), `omfdump.py` (MSC-OMF inkl. 0x9C-Fixups),
  `match.py` (Reloc-Maskierung), `verify.py` (Ledger-Recheck), `coverage.py`
  (Byte-Metrik), `report.py` (erzeugt diese Datei), `markcrt.py` (CRT-Signaturen).

## Offen (Reihenfolge fuer die naechsten Runden)

1. **Integritaetsloch schliessen:** `verify.py` prueft gegen die gerade in
   `build/` liegenden OBJ-Dateien, baut sie nicht neu. Nach jeder Quellaenderung
   kann ein Ledger-Eintrag unbemerkt gegen ein anderes Kompilat laufen. Fix:
   `verify.py` soll `build.py` mit den im Ledger vermerkten Flags aufrufen.
2. `LINK.EXE` (DOSX16) haengt unter dosbox-x in allen DPMI-Varianten — Voraussetzung
   fuer `build_replacement` (Phase 6); Kandidat: nativer OMF-Linker (jwlink)
3. Slot-Subsystem: `__asm`-Rekonstruktion erwaegen (dort ist C nachweislich erschoepft)
4. Weiter im Familien-Workflow: ALU-/DOS-Helfer mit `55 8b ec`-Rahmen
<!-- MANUAL-END -->
