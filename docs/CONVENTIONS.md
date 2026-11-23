# dds98 — Konventionen & Parameter

Gilt für das Byte-Match-Projekt zu **Giten Megami Tensei** (Spiel-Engine `DDS98.EXE`).

## Parameterblock (Stand: Runde 1, 2026-11-23)

| Parameter         | Wert                                                                                                                  | Beleg |
|-------------------|-----------------------------------------------------------------------------------------------------------------------|-------|
| `<NAME>`          | `dds98`                                                                                                               | Engine-Binary |
| `<BINARY>`        | `giten\DDS98\DDS98.EXE` — 480 710 B, Stand 10.03.1997                                                                 | Retail (das installierte Spiel) |
| `<BIN_FORMAT>`    | **MZ** (16-Bit-DOS-EXE); Load-Image endet bei Dateioffset 339 735; 3 562 Relocations; **Overlay ≈ 141 KB** (beginnt mit Nullbytes, Inhalt offen) | MZ-Header |
| `<ARCH>`          | x86-16, **Real Mode**; CPU-Basis (8086/186/386 → `/G0|/G1|/G2`) per Idiom-Scan festnageln                            | Ghidra `x86:LE:16:Real Mode` |
| `<LOAD_BASE>`     | Ghidra-Abbildung **`0x1000:0000`** (linear `0x10000`); Entry **`0x1871:0BE5`** (Header `CS:IP 0871:0BE5`)              | MZ-Header + `DDS98_functions.txt` („entry") |
| `<DISASM_EXPORT>`| Ghidra 12.2 PUBLIC — Projekt `ghidra_proj\GitenDecomp.gpr`, C-Export `decompiled\DDS98_decompiled.c` (1 970 Fkt.)      | vorhanden |
| `<TOOLCHAIN>`     | **Kandidat: Microsoft C 8.00x (16-Bit, 1992/93)** — Binary enthält `MS Run-Time Library - Copyright (c) 1992, Microsoft Corp` + `run-time error`-Tabelle. Exakte Version/Linker: **Phase 0 per Kalibrier-Kompilierung**, nicht raten | CRT-Strings |
| `<CFLAGS>`        | **Phase 0.** Sicher: kein tiny/small — Startup setzt `DS=0x58FC ≠ CS` → mindestens compact/medium; exaktes Memory-Modell + Optimierung per Kalibrierung | dekompiliertes Startup (FUN_1000_0010) |
| `<OBJ_DUMP>`      | Objektformat wird **OMF** sein → `wdis` (Open Watcom) / `tdump` (Borland) als Reader, sonst eigenes `tools/omfdump.py`   | folgt aus Toolchain |
| `<HOST>`          | Windows x64; MSC 8 läuft nur unter DOS → **DOSBox-Wrapper im Build-Skript kapseln**                                    | System |

## Adressen
- Ghidra-Abbildung: `SSSS:OOOO`, linear = `seg*16+off`; Bildbasis `0x1000:0000` = linear `0x10000` = Dateioffset `0x3800` (MZ-Header, 896 Paragraphen).
- Dateioffset = `linear − 0x10000 + 0x3800`, gültig bis Offset 339 735 (danach Overlay).
- MZ ist laufzeit-relocierbar (3 562 Relocs): Vergleiche immer **image-relativ gegen die Ghidra-Abbildung**; welche Bytes Linker-Operanden sind, **aus der Objekt-Relocation-Tabelle lesen**, nie raten.

## Ledger (`docs/MATCHING.md`)
Eine Zeile pro Adresse, Duplikate verboten, Größe ≠ 0:
`| va (seg:off) | name | size | status | note |` mit Status ∈ `MATCH | RELOCS | PENDING`.

## Build — verifiziertes Rezept (2026-11-23)
`build.py` kapselt: **dosbox-x** (v2026.08.31, VS/SDL1-64-Bit) mit `-nopromptfolder`
+ **HDPMI32** (HX-DOS-Runtime 2.17) als DPMI-Server-TSR **vor** jedem CL-Aufruf
+ `cycles=max` + SDL-Dummy-Treiber + APPDATA-Redirect nach `dosboxx_home\`.

Warum nicht DOSBox 0.74: MSC7s CL ist ein DOSX32-Protected-Mode-Programm;
0.74 liefert `run-time error R6901` (kein DPMI). dosbox-x' eingebautes DPMI
crasht mit MSC7 (GitHub-Issue #3844) — **HDPMI ist die verifizierte Lösung**.
Nachweis: `python build.py src/calib/triv1.c --flags "/G1 /AL"` →
480-Byte-OMF-Objekt (THEADR-Record mit Quelldatei).

Deko-Historie: die Disketten-Dateien sind KWAJ-komprimiert; `DECOMP.EXE`
(Profiler-Diskette) in DOSBox 0.74 dekomprimiert (224/224, ~0,14 s/Datei).

## Offen (Phase 0)
1. CFLAGS-Kalibrierung gegen **echte** DDS98-Funktionen (`/G1` + `/AH` vs `/AL`) — Compiler läuft, Byte-Vergleiche offen
2. OMF-Adapter für `match.py` (Symbol- + RELOC-Extraktion aus dem Objekt) — `wdis`/`tdump` oder eigenes `tools/omfdump.py`
3. Overlay-Inhalt (≈141 KB) über die Laderoutinen klären

## Fremdcode (Phase 1, getrennt führen)
MS-C-CRT (Nachweis: Runtime-Banner in der Binary) als Bibliothek markieren und **nicht** decompilieren, sobald die CRT-Region per Kalibrier-Kompilierung abgesteckt ist.

## Phase-0-Evidenz (ScanIdioms-Lauf, 2026-11-23, 68 452 Instruktionen)

**CPU-Basis: 80186/80286 — kein 386.** `PUSHA` 17, `POPA` 13, `ENTER` 600, `LEAVE` 1315,
`IMUL` (reg-Form) 100, `INSB/OUTSB` vorhanden; `0x66`-Präfix nur 8× (Rauschen/Daten),
`0x67` = 0. → Kalibrier-Kandidat **`/G1`** (80186); `/G2` nur, falls ein echtes
286-Idiom auftaucht.

**Memory-Modell: large/huge.** 2 907 near-`CALL` vs 1 760 `CALLF`, 1 348 `RETF`;
Code ≈ 306 KB über mehrere 64-K-Segmente; DGROUP (`DS=0x58FC`) bis Bildende
(Paragraph `0x71E7`) ≈ 102 KB > 64 KB → **Tendenz `/AH` (huge)**; `/AL` nicht
ausgeschlossen (Kalibrier-Kompilierung klärt exakt).
Bildlayout (Paragraphen): Code `0–0x52B1`, Stack `0x52B1–0x58FC` (`SS:SP=52B1:1000`),
Daten `0x58FC–0x71E7`.

**crt0 = Microsoft-C-16-Bit-Familie (bestätigt).** Entry `0x1871:0BE5`:
`PUSH DS/ES; MOV AX,CS; MOV DS,AX; MOV [0x5],ES; ADD AX,0x10; MOV [0x9],AX`
(sichert PSP-Segment und `PSP+0x10` in DGROUP), `MOV AH,30; INT 21h` (DOS ≥ 3),
`MOV ES,ES:[0x2C]` (PSP-Umgebungssegment) — klassische MSC-8-Startup-Sequenz.
Exakte Version: erst Kalibrier-Kompilierung.

**Overlay (≈141 KB ab Offset 339 735):** dichter Binär-Payload — 74 % Nichtnull,
alle 4-K-Blöcke belegt, keine Archiv-/MZ-Signatur, keine ASCII-Strings, kein
Selbst-Pfad-Verweis in der Binary. Vermutung: zur Laufzeit gelesene Daten;
Klärung über die Laderoutinen, `extract_*`-Werkzeug bei Bedarf.

**Build-Stempel in der Binary:** `DDS98 date=%s, time=%s` (linear `0x59038`).
