# PROGRESS

## Runde 24 — Integritaetsloch geschlossen: verify baut selbst (2026-11-23)
- Ledger-Format kanonisiert: jede MATCH/RELOCS-Zeile traegt
  `src=<quelldatei>; flags="<cflags>"` — verify.py liest das und **kompiliert jede
  (src, flags)-Kombination neu**, statt sich auf vorhandene `build/*.OBJ` zu verlassen.
- Beweis: `build/*.OBJ` geloescht -> verify baute alle 6 Quelldateien und meldete
  14/14 RELOCS ok, PENDING 5, gruen. Vorher haette derselbe Lauf gegen veraltete
  oder fremde Kompilate geprueft (Runde-23-Befund).
- `--fast` ueberspringt den Neubau bewusst (nur Zwischencheck, nie Close-out).
- Duplikat- und Groesse-0-Pruefung bleibt im Verify (Vorlage Phase 6).

## Runde 23 — Optimierungsstufe als Codegen-Klasse entdeckt (2026-11-23)
- Familien-Scan mit maskierten disp16: 3 Gruppen. Die groesste (3dd3:0000..) ist
  ein **Segment-Alias** der bereits gematchten Getter (linear identisch mit
  35ca:8090) — Lehre: Linearadresse ist die Identitaet, sonst Doppelzaehlung.
- Clamp-Geschwister (1f2d:000e / 1f2f:0002, 2x20 B) entschluesselt: min(max(x,1),g)
  mit __fastcall und DX-Temp. 6 Varianten getestet, MSC7 erzeugt weder
  rahmenlos+DX (Original) — PENDING.
- **Hauptfund:** `/Oy` und `/Ox` entfernen den Rahmen; alle bisherigen Matches
  nutzten `/Os`. `/Ox` brachte get_39f8_clamped auf 14/16 B (Rest: `C3 90` vs
  `EB 03`, also Early-Return+Pad statt Sprung-Merge). Flags sind pro Quelldatei
  zu waehlen — als Regel in IDIOMS.md festgehalten.
- CONV unter /Ox gegengeprueft: `D1 E3` bleibt (Hand-ASM-Verdacht dort bestaetigt).
- Integritaetsloch notiert: verify.py baut nicht neu, prueft die vorhandenen OBJs.

## Runde 22 — report.py: STATUS.md wird generiert (2026-11-23)
- `tools/coverage.py` in `compute()` (Zahlen) + `main()` (Konsolenausgabe) getrennt,
  damit `tools/report.py` dieselben Zahlen ohne Doppel-Logik nutzen kann.
- `tools/report.py` schreibt `docs/STATUS.md`: Ledger-Zaehler (MATCH/RELOCS/PENDING),
  PENDING-Liste, Coverage-Tabelle, Regions-Tabelle. Handgeschriebener Teil steht
  zwischen `MANUAL-BEGIN`/`MANUAL-END` und bleibt bei jedem Lauf erhalten (getestet).
- Damit sind die Zaehler nicht mehr handgepflegt — STATUS kann nicht mehr
  veralten oder widerspruechlich werden (die Ursache der Runde-21-Bereinigung).
- verify gruen, Coverage-Zahlen unveraendert (100 / 293 640 B = 0,034 %).

## Runde 21 — Inventar bereinigt: 1956 Code-Funktionen statt 1970 (2026-11-23)
- `functions.csv` traegt jetzt `section=CODE|DATA`; `gt.py` setzt die Markierung aus
  `not_code.csv`, `coverage.py` zaehlt nur CODE-Zeilen als Funktionen.
- Zeilen bleiben erhalten (Groesse haengt am Abstand zur naechsten Funktion) —
  geloescht wird nichts, nur klassifiziert. Eine Quelle statt zwei Zaehlwegen.
- Zahlen unveraendert korrekt: 294 603 Code-Bytes − 963 CRT = 293 640 Eigenbytes,
  100 verifiziert (0,034 %); Funktionszahl jetzt ehrlich 1 956 + 14 Daten.
- verify gruen (17 Zeilen), kein Ledger-Eintrag faelschlich als DATA markiert.

## Runde 20 — zwei RELOCS + zwei neue Idiom-Regeln (2026-11-23)
- OR_JOIN (20b2:0000): `void: g_or |= x` — der Diff `09` vs `0B` war die
  Zuweisungsrichtung (or r/m,r = Store vs. or r,r/m = Return), nicht der Ausdruck.
- _wait_change (20ab:000c): Spin-Wait auf `volatile int` — ohne volatile hoistet
  MSC7 den Loop-Load (18 B, degenerierter cmp), mit volatile steht der Reload im
  Schleifenkopf und trifft das Original inkl. `74 F8` exakt (20 B).
- verify.py reicht jetzt die **Ledger-Groesse** an match.py durch (--size):
  Ledger-Groesse ist laut Vorlage die echte Laenge; Inventarfenster, die in die
  Folge-Funktion laufen (hier 18 statt 14 B), verfaelschen sonst den Vergleich.
- Stand: 14 RELOCS / 3 PENDING, 100 von 293 640 Eigencode-Bytes (0,034 %).

## Runde 19 — 12 211 Bytes Fehlinventarisierung als Daten klassifiziert (2026-11-23)
- Die 38 Ghidra-Dekompilierungsfehler sortiert: 14 Eintraege nachweislich kein
  Code — CD-3F-Soundtreiber-Befehlsbloecke (NMUSE/MIDE, 6-Byte-Stride), lineare
  Wort-Tabellen, 10,9-KB-Nullfeld, ASCII-String 'num err floor'.
- ground_truth/not_code.csv + coverage.py-Datenkategorie: Metrik jetzt dreifach
  ehrlich — 293 640 Eigencode-Bytes (statt 306 814), 66 verifiziert.
- ~24 weitere FAILs sehen nach echten Funktionen aus (ENTER-Rahmen, Parameter-
  loads) — Kandidaten fuer spaetere Runden.

## Runde 18 — conv entschlusselt: 14/16 Byte, Muster-These Hand-ASM (2026-11-23)
- 458e:a1ea == inc_39f8_capped (schon RELOCS ✓) — 'slot_update' gratis.
- 4fad:0006 (CONV, 16 B, near-pascal Lookup): 5 Quellformen + 3 Opt-Stufen —
  /Os matcht ALLES bis auf 2 Bytes (shl vs add bx,bx). Frame-Kompaktion
  (push bp/mov bp,sp statt ENTER) im Original bestaetigt und reproduziert.
- Muster-These gereift: das Slot-Subsystem (4 Funktionen) traegt konsistent
  Hand-ASM-Idiome — dokumentiert in IDIOMS.md als Arbeitsgrundlage.

## Runde 17 — Slot-Routine: Form entschuesselt, 4 Hypothesen, PENDING (2026-11-23)
- 458e:a20e (166 B, pascal, Far-Param) vollstaendig zerlegt: Slot-Index-Flow,
  8 Feldoffs 0/2/4/9/11/13/15/19, conv-CL-Push, retf 4 (=1 Far-Param, Ghidras
  param_2 war Artefakt). Ungerade Slotgroesse 0x27 -> char-Array, kein struct.
- Rekonstruktion v3 erreichte 162/166 B — Restdifferenz: Registerwanderung ohne
  Stack-Rueckschreibung (MSC7-C schreibt Param zurueck). PENDING mit Formanalyse
  in IDIOMS.md; cslot1.c behaelt v3 als naechsten Ansatzpunkt.
- Praxisecke: __pascal versaliert Symbole; >127-Sprungdistanz erzeugt die
  jge+3/jmp-Form automatisch (Branch-Erklaerung fuer 4fab:000a-Verwandtschaft).

## Runde 16 — PENDING-Semantik bewiesen (2026-11-23, Abend)
- Aufrufer von 4fab:000a gefunden (FUN_458e_a20e): Slot-Index-Allokator,
  Sentinel -1 wird geprueft, Slots 0x27 Byte, Array-Basis DGROUP-relativ
  (-0x6d58). Sprung-Merge bleibt Hand-ASM-Verdacht — PENDING-Notiz vertieft.
- FUN_458e_a20e selbst (52 B Slotfuell-Routine) ist ein Kandidat fuer die
  naechste Familien-Runde: Parameter, Feldschreibzugriffe, RTC-lose Form.

## Runde 15 — Coverage trennt Fremdcode (2026-11-23, abends)
- coverage.py zeigt 'Fremd-CRT'-Spalte: 963 B (35 eindeutige Bibliothekssignaturen)
  werden von der Eigenbyte-Metrik abgezogen — Prozent jetzt gegen Eigenbytes
  (66/305851 = 0,022 %). CRT-Anteil waechst mit weiteren Signaturtreffern.

## Runde 13 — CRT-Region abgesteckt (2026-11-23)
- markcrt.py repariert: MS-Librarian richtet Module aus (Padding nach MODEND)
  — Scan zum naechsten THEADR; jetzt 379/379 Module aus MLIBCR.LIB.
- **35 eindeutige CRT-Treffer** (reloc-maskierte Bibliothekssignaturen) in
  DDS98.EXE, ab 10bd:0002 aufwaerts: __int86/_abs/_srand/__NMSG_WRITE/__dos_setvect …
  -> ground_truth/foreign_crt.csv. CRT liegt am Bildanfang (Linker-Reihenfolge).
- Offen fuer naechste Session: coverage.py um Fremdcode-Spalte ergaenzen,
  CRT-Byteanteil in der ehrlichen Metrik separat ausweisen.

## Runde 11 — coverage.py + PENDING-Vertiefung (2026-11-23)
- get_39f8_clamped: 5 Konstrukt-/Opt-Kombis ausgereizt (Ternaer x2, if/else+r,
  /O1, /O2) — MSC7 erzeugt die Sprung-Merge-Form nie aus C. PENDING mit
  Hand-/Inline-ASM-Verdacht dokumentiert; Beweis via Aufrufer-Kontext spaeter.
- coverage.py gebaut (Vorlage Phase 6): Bytes pro 64-KiB-Region gegen das
  Original-Inventar — die ehrliche Metrik betraegt 66/306814 Bytes (0,022 %).

## Runde 10 — 0x39F8-Paar: 1 RELOCS, 1 ehrliches PENDING (2026-11-23)
- inc_39f8_capped (4fac:000a): RELOCS — `if (g<0x10) g++;` Form exakt.
- get_39f8_clamped (4fab:000a): PENDING — MSC7-/Os kompiliert Ternaer zur
  Early-Return-Form; das Original benutzt Sprung-Merge mit einem RET. Zwei
  Hypothesen (Ternaer, if/else+r) dokumentiert; dritte folgt mit Aufrufer-Kontext.
- IDIOMS.md erstmals mit verifizierten MSC-Idiomen befuellt (Vorlage 4: nach
  jeder geloesten Diff-Ursache ergaenzen — hier: die ungeloesste auch).
- verify: gruen — 13 Ledger-Zeilen, RELOCS 12, PENDING 1.

## Runde 9 — 32-Bit-Getter-Paar + Flag-Op: 11 RELOCS gesamt (2026-11-23)
- cget3.c: get_l (far) + get_ln (__near) — DX:AX-Rueckgabe, je 2x disp16-Fixup,
  Original 1871:d0e4 / 35ca:3c34 (Ghidra hatte get_l als 16-Bit fehltypisiert).
- cflag1.c: set_flag = or byte [0x0F44],0x40 — Einzelmitglied, Bereich <=8 Bytes
  damit vollstaendig klassifiziert (GET 8, Paar 2, Flag 1).
- verify: gruen, Ledger 11 Zeilen, 0 PENDING.

## Runde 8 — GET-Familie komplett: 8/8 RELOCS (2026-11-23)
- Familien-Scan (Funktionen <=8 Bytes nach Codeform): GET-Familie hat 8 Mitglieder.
- Teil 2 (cget2.c): vier Einzelscalar-Getter auf DGROUP 0x1A4/0x2FCE/0x2C50/0x2D0C —
  alle vier RELOCS; verify: gruen, Ledger 8 Zeilen, 0 PENDING.
- omfdump: kompakte 0x9C-Fixups mit variabler Eintraglaenge (3/4 Byte, Zielindex).

## Runde 7 — Phase 0 ABGESCHLOSSEN: 4 byte-verifizierte Funktionen (2026-11-23)
- **Erste RELOCS-Matches**: Getter-Familie 35ca:8090..9c (get0..get3),
  `mov ax,[disp16]; retf` — disp16 als einziger maskierter Linker-Fixup.
- **CFLAGS bestätigt: `/G1 /AM /Gs /Os`** (Medium-Modell; /Gs = keine chkstk-
  Prologen im Original; /Os = Bare-Leaf-Form; /G1 = 186-Idiome).
  Korrektur: fruehere huge/large-Vermutung falsch (Near-Daten-Beweis).
- match.py komplett: OMF-Extraktion (omfdump.py) + Reloc-Maskierung + Klassifikation.
  MSC7-Fixups laufen als kompakte 0x9C-Records (COMENT-class-A2-Erweiterung).
- verify.py steht, laeuft gruen: Ledger 4 Zeilen, 4 RELOCS, 0 PENDING.
- Praxisecke: CL stirbt lautlos bei Quelldateien >8.3 Zeichen (Kalibrierquelle
  umbenannt cget.c); LINK.EXE (DOSX16) unter dosbox-x bislang unbrauchbar (haengt
  in allen DPMI-Varianten) — Phase-6-Thema.

## Runde 5/6 — Toolchain-Durchbruch (2026-11-23, 01:35)
- **MSC 7.0 (CL 8.00) kompiliert**: `triv1.c /G1 /AL` → 480-Byte-OMF-Objekt.
- Verifiziertes Rezept: dosbox-x + HDPMI32-TSR (HX-DOS 2.17) + `-nopromptfolder`
  + APPDATA-Redirect + `cycles=max`. DOSBox 0.74: R6901/kein DPMI; dosbox-x-eigenes
  DPMI crasht mit MSC7 (GitHub-Issue #3844).
- `build.py` auf das Rezept umgestellt, End-to-End über sich selbst verifiziert.
- Toolchain-Deko komplett: 224/224 Dateien aus den KWAJ-Disketten (DECOMP unter
  DOSBox 0.74; Erkenntnisse: BAT ohne `CALL` frisst die restliche Autoexec;
  Hintergrund-Jobs lassen DOSBox-0.74-Kinder hängen — nur Vordergrundläufe).

## Runde 1 — 2026-11-23
- Parameterblock belegt und in `CONVENTIONS.md` festgehalten (MZ, x86-16 Real Mode,
  Load-Image/Overlay-Geometrie, MSC-8-Kandidat via CRT-Banner, Entry `0x1871:0BE5`).
- Skelett angelegt: `include/dds98 src tests tools docs ground_truth`.
- `tools/`: `gt.py` (Inventar), `disasm.py` (Hexdump + Ghidra-Instruction-Dump),
  `match.py` (Byte-Match-Kern mit Selbsttest; BUILD-Schritt bricht bis Kalibrierung
  kontrolliert ab), `ghidra_run.py` (Headless-Starter mit APPDATA-Sandbox-Workaround),
  `build.py` (Stub, `TOOLCHAIN_NOT_CALIBRATED`).
- Phase-0-Scans ausgewertet (ScanIdioms, 68 452 Instruktionen): CPU-Basis 80186+
  (`/G1`-Kandidat), Memory-Modell large/huge (Tendenz `/AH`, DGROUP ≈ 102 KB),
  crt0-Sequenz am Entry `0x1871:0BE5` bestätigt Microsoft-C-16-Bit.
- Overlay analysiert: dichter Binär-Payload (~141 KB), keine Archiv-Signatur,
  kein Selbst-Pfad-Verweis — Klärung über Laderoutinen später.
- match.py-Selbsttest grün (MATCH/RELOCS/DIFF-Kern, Reloc-Maskierung, Längendiff).
- Offen: Toolchain-Beschaffung (MSC 8/MSVC 1.5x + DOSBox) — Freigabe des Nutzers nötig;
  danach Kalibrier-Kompilierung (Phase 0) und erste MATCH-Runde.
