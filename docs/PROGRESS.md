# PROGRESS

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
