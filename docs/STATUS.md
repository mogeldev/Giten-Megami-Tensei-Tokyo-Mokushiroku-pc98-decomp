# STATUS

<!-- GENERIERT von tools/report.py am 2026-11-23 — Zahlen nicht von Hand -->
<!-- Handgeschriebener Teil zwischen MANUAL-BEGIN und MANUAL-END bleibt erhalten. -->

## Ledger (Quelle: docs/MATCHING.md)

| Status | Anzahl |
|---|---|
| MATCH | 0 |
| RELOCS | **14** |
| PENDING | **7** |

PENDING-Faelle (Details in `docs/MATCHING.md`, Idiome in `docs/IDIOMS.md`):

- `4fab:000a` **get_39f8_clamped** (16 B) — Slot-Index-Allokator (Aufrufer FUN_458e_a20e: Sentinel -1, Slots 0x27 B). Beste Variante /Ox: 14/16 B — Restdiff `C3 90` (Early-Return + Padding) vs. 
- `1f2d:000e` **CLAMP_A** (20 B) — min(max(x,1),g), __fastcall (Arg in AX, nacktes retn), Global 0x4688. Original rahmenlos mit DX-Temp (`8B 16 d / 3B C2 / 7E 02 / 8B C2`)
- `1f2f:0002` **CLAMP_B** (20 B) — Geschwister von CLAMP_A, Global 0x468A, gleiche Ursache
- `352a:0004` **reset_9b30** (22 B) — g1=0
- `4527:000a` **reset_9b30b** (22 B) — Duplikat-Body von reset_9b30 (zweite Code-Kopie), gleiche Ursache
- `458e:a20e` **SLOT_FILL** (166 B) — Slotfuellroutine (pascal, 1 Far-Param). Beste Variante 162/166 B
- `4fad:0006` **CONV** (16 B) — Lookup table[c] (Wort-Tabelle DGROUP 0x396A, near-pascal). /Os liefert alles identisch bis auf 2 B: `D1 E3` (shl bx,1) statt `03 DB` (add bx,bx)

## Coverage (ehrliche Byte-Metrik)

| Kategorie | Wert |
|---|---|
| Inventar-Einträge | **1956** Code-Funktionen + **14** Daten |
| Daten (belegt, `not_code.csv`) | 12211 B |
| Code-Bytes | 294603 |
| − Fremd-CRT (Signaturen) | 963 |
| = **Eigencode-Bytes** | **293640** |
| davon **verifiziert** | **100 (0.034%)** |
| PENDING-Bytes | 282 |

Code-Funktionen: **1956**, davon verifiziert **14**.

## Regionen (64 KiB)

| Region | Funktionen | ok | Code-B | verifiziert | CRT | Daten | PENDING |
|---|---|---|---|---|---|---|---|
| 0x0000 | 534 | 1 | 65244 | 4 (0.0%) | 897 | 360 | 40 |
| 0x0001 | 406 | 4 | 65783 | 48 (0.1%) | 0 | 569 | 0 |
| 0x0002 | 545 | 5 | 65692 | 24 (0.0%) | 0 | 0 | 22 |
| 0x0003 | 429 | 4 | 64548 | 24 (0.0%) | 0 | 0 | 220 |
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

1. **MSC 6.0 beschaffen und Phase-0-Kalibrierung wiederholen** — die haeufigsten
   Codegen-Formen des Originals (`add bx,bx` 74x, Zero-Immediate-Stores 130x)
   erzeugt MSC 7.0 in keiner Flagskombination (s. `docs/CONVENTIONS.md`). Erst
   danach neue PENDINGs als Hand-ASM einordnen.
2. `LINK.EXE` (DOSX16) haengt unter dosbox-x in allen DPMI-Varianten — Voraussetzung
   fuer `build_replacement` (Phase 6); Kandidat: nativer OMF-Linker (jwlink)
3. Build-Cache (Flags+mtime) fuer `verify.py`, damit der Rebuild nicht jedes Mal
   ~25 s kostet (Vorlage Phase 3 nennt den Cache ausdruecklich)
4. Weiter im Familien-Workflow: ALU-/DOS-Helfer mit `55 8b ec`-Rahmen
<!-- MANUAL-END -->
