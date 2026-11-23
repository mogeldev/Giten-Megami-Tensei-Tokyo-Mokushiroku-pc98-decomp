# STATUS

<!-- GENERIERT von tools/report.py am 2026-11-23 — Zahlen nicht von Hand -->
<!-- Handgeschriebener Teil zwischen MANUAL-BEGIN und MANUAL-END bleibt erhalten. -->

## Ledger (Quelle: docs/MATCHING.md)

| Status | Anzahl |
|---|---|
| MATCH | 0 |
| RELOCS | **14** |
| PENDING | **3** |

PENDING-Faelle (Details in `docs/MATCHING.md`, Idiome in `docs/IDIOMS.md`):

- `458e:a20e` **SLOT_FILL** (166 B) — Slotfuellroutine (pascal, 1 Far-Param, 8 Felder 0/2/4/9/11/13/15/19, conv+update-Calls). 4 Hypothesen: v3 (162/166 B!) fehlen nur die Stack-Rueckschre
- `4fad:0006` **CONV** (16 B) — Lookup table[c] (Wort-Tabelle DGROUP 0x396A, near-pascal). 5 Quellformen + /Od-/O1-/O2 getestet: /Os liefert ALLES identisch (55 8b ec-Rahmen, [bp+4],
- `4fab:000a` **get_39f8_clamped** (16 B) — Aufrufer FUN_458e_a20e beweist Semantik: Slot-Index-Allokator (Zaehler DGROUP 0x39F8, max 16, Slotgr. 0x27, Sentinel -1 wird geprueft via `if (-1 < iV

## Coverage (ehrliche Byte-Metrik)

| Kategorie | Wert |
|---|---|
| Inventar-Einträge | **1956** Code-Funktionen + **14** Daten |
| Daten (belegt, `not_code.csv`) | 12211 B |
| Code-Bytes | 294603 |
| − Fremd-CRT (Signaturen) | 963 |
| = **Eigencode-Bytes** | **293640** |
| davon **verifiziert** | **100 (0.034%)** |
| PENDING-Bytes | 198 |

Code-Funktionen: **1956**, davon verifiziert **14**.

## Regionen (64 KiB)

| Region | Funktionen | ok | Code-B | verifiziert | CRT | Daten | PENDING |
|---|---|---|---|---|---|---|---|
| 0x0000 | 534 | 1 | 65244 | 4 (0.0%) | 897 | 360 | 0 |
| 0x0001 | 406 | 4 | 65783 | 48 (0.1%) | 0 | 569 | 0 |
| 0x0002 | 545 | 5 | 65692 | 24 (0.0%) | 0 | 0 | 0 |
| 0x0003 | 429 | 4 | 64548 | 24 (0.0%) | 0 | 0 | 198 |
| 0x0004 | 42 | 0 | 33336 | 0 (0.0%) | 66 | 11282 | 0 |

<!-- MANUAL-BEGIN -->
## Toolchain

- **MSC 7.0 (CL 8.00, 1992)**: dosbox-x + HDPMI32-TSR, `-nopromptfolder`,
  APPDATA-Redirect, `cycles=max` — Rezept in `docs/CONVENTIONS.md`.
- CFLAGS **bestaetigt: `/G1 /AM /Gs /Os`** (byte-identische Kalibrierfunktionen).
- Werkzeuge: `build.py` (kompiliert), `omfdump.py` (MSC-OMF inkl. 0x9C-Fixups),
  `match.py` (Reloc-Maskierung), `verify.py` (Ledger-Recheck), `coverage.py`
  (Byte-Metrik), `report.py` (erzeugt diese Datei), `markcrt.py` (CRT-Signaturen).

## Offen (Reihenfolge fuer die naechsten Runden)

1. `LINK.EXE` (DOSX16) haengt unter dosbox-x in allen DPMI-Varianten — Voraussetzung
   fuer `build_replacement` (Phase 6); Kandidat: nativer OMF-Linker (jwlink)
2. Slot-Subsystem: `__asm`-Rekonstruktion erwaegen (dort ist C nachweislich erschoepft)
3. Weiter im Familien-Workflow: ALU-/DOS-Helfer mit `55 8b ec`-Rahmen
<!-- MANUAL-END -->
