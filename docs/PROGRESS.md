# PROGRESS

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
