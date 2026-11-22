# PROGRESS

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
