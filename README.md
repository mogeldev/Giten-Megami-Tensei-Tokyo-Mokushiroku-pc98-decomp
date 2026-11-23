# Giten Megami Tensei: Tokyo Mokushiroku — DDS98.EXE-Decompilation

Byte-exakte Rekonstruktion der Spiel-Engine **DDS98.EXE** (偽典・女神転生 ～東京黙示録～,
1997) nach dem Workflow für byte-verifizierte Decompilierung:
Jede Funktion ist **MATCH** (byte-identisch), **RELOCS** (identisch bis auf echte
OMF-Linker-Relocations) oder **PENDING** mit dokumentierter Ursache — nichts wird gefaked.

## Status (2026-11-23)

- **Phase 0 abgeschlossen** — Original-Toolchain: **Microsoft C/C++ 7.0** (CL 8.00, 1992),
  kompiliert unter dosbox-x mit HDPMI (HX-DOS-Runtime) als DPMI-Server.
- Bestätigte Flags: **`/G1 /AM /Gs /Os`** (80186-Basis, Medium-Modell, keine
  Stackchecks, Größenoptimierung) — nachgewiesen an byte-identischen Kalibrierfunktionen.
- **12 Funktionen byte-verifiziert** (RELOCS), 1 PENDING (Sprung-Merge-Polarität,
  fünf getestete Konstrukte dokumentiert).
- Coverage: **66 / 306 814 Code-Bytes (0,022 %)** — die ehrliche Byte-Metrik aus
  `tools/coverage.py`, nicht die Funktionszahl.

## Struktur

```
docs/           CONVENTIONS (Parameter+Evidenz), MATCHING (Ledger), IDIOMS, PROGRESS, STATUS
ground_truth/   functions/strings/imports + foreign_crt (Fremdcode-Signaturen)
src/calib/      rekonstruierte Quellen (8.3-Namen — MSC-CL-1992-Pflicht)
tools/          gt (Inventar), build (DOSBox-x-Rezept), omfdump, match, verify, coverage, markcrt
```

## Bauen

Benötigt Microsoft C/C++ 7.0 (Abandonware, z. B. via archive.org) und dosbox-x +
HX-DOS-Runtime. Das komplette Rezept inklusive aller Fallen steht in
`docs/CONVENTIONS.md`: HDPMI32-TSR vor jedem CL-Aufruf, `-nopromptfolder`,
APPDATA-Redirect, 8.3-Quelldateinamen, `cycles=max`.

**Kein Original-Material in diesem Repo:** die Binary, die Toolchain und die
dekompilierten Rohauszüge liegen bewusst außerhalb — hier stehen nur eigene
Rekonstruktionen, Werkzeuge und Dokumentation.
