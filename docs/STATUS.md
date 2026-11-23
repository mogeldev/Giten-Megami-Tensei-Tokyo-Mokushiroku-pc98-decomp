# STATUS

(vorerst handgeführt; ab regelmäßigem Betrieb erzeugt `tools/report.py` diese Datei)

- implementiert & MATCH/RELOCS: **0**
- PENDING: **0**
- bekanntes Inventar: **1970** Funktionen (`ground_truth/functions.csv`);
  38 davon hatte Ghidra-Dekompilierungsfehler → zuerst klären (meist Daten-als-Code).
- Fremdcode-Region (MS-C-CRT): **Region noch nicht abgesteckt** — crt0-Sequenz am Entry
  ist als MSC-16-Bit-Familie identifiziert (siehe CONVENTIONS.md Phase-0-Evidenz).
- Phase-0-Evidenz steht: CPU 80186+ (`/G1`), large/huge (Tendenz `/AH`), MSC-crt0.
- **Toolchain lauffähig:** MSC 7.0 kompiliert via dosbox-x + HDPMI32 (CONVENTIONS.md).
  Offen: CFLAGS-Kalibrierung gegen echte Binary-Funktionen + OMF-Adapter für match.py.
- Coverage: **0 %**. Erstes Ziel: CRT abstecken + erste kleine Familie
  (String-/DOS-Helfer) vollständig matchen statt zehn halber Funktionen.
