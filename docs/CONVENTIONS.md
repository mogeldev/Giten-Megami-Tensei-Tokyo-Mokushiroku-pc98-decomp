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
| `<CFLAGS>`        | **bestätigt: `/G1 /AM /Gs /Os`** (Kalibrier-Familie 35ca:8090..9c, 4× RELOCS). Medium-Modell: near-Daten + far-Code; `/Gs` (keine Stackchecks — das Original trägt keine chkstk-Aufrufe); `/Os` (Bare-Leaf-Form ohne toten ENTER-Rahmen); `/G1` (186-Idiome) | match.py, 2026-11-23 |
| `<OBJ_DUMP>`      | Objektformat wird **OMF** sein → `wdis` (Open Watcom) / `tdump` (Borland) als Reader, sonst eigenes `tools/omfdump.py`   | folgt aus Toolchain |
| `<HOST>`          | Windows x64; MSC 8 läuft nur unter DOS → **DOSBox-Wrapper im Build-Skript kapseln**                                    | System |

## Adressen
- Ghidra-Abbildung: `SSSS:OOOO`, linear = `seg*16+off`; Bildbasis `0x1000:0000` = linear `0x10000` = Dateioffset `0x3800` (MZ-Header, 896 Paragraphen).
- Dateioffset = `linear − 0x10000 + 0x3800`, gültig bis Offset 339 735 (danach Overlay).
- MZ ist laufzeit-relocierbar (3 562 Relocs): Vergleiche immer **image-relativ gegen die Ghidra-Abbildung**; welche Bytes Linker-Operanden sind, **aus der Objekt-Relocation-Tabelle lesen**, nie raten.

## Phase-0-Befund Runde 25 — Compiler-Generation pruefen (offener Punkt!)
Byte-Statistik der Original-Binary (Load-Image, 294 603 Code-Bytes):

| Muster | Original | MSC 7.0 (/Os) | Bewertung |
|---|---|---|---|
| `03 DB` (add bx,bx) | **74x** | erzeugt `D1 E3` (shl) | Original nutzt ADD |
| `D1 E3` (shl bx,1) | 18x | Standard bei MSC7 | selten im Original |
| `C7 06 .. 00 00` (Zero-Immediate-Store) | **130x** | /Os faltet zu `33 C0 A3` | Original nutzt Immediate |
| `33 C0 A3` (Zero-Fold) | 32x | Standard bei MSC7 /Os | selten im Original |
| `55 8B EC` (Rahmen) | 1184x | /Os erzeugt Rahmen | passt zu /Os |

Die beiden haeufigsten Codegen-Formen des Originals (`add bx,bx`, Zero-Immediate)
erzeugt MSC 7.0 in keiner getesteten Flagskombination; gleichzeitig passt die
Rahmen-Dichte zu /Os. Arbeitshypothese: **Spielmodule mit MSC 6.x uebersetzt,
gegen CRT 7 gelinkt**. Naechster Phase-0-Schritt: MSC 6.0 beschaffen, Kalibrier-
Familien damit wiederholen. Erst danach neue PENDINGs als Hand-ASM einordnen —
sonst wird eine falsche Toolchain-Annahme als "Hand-ASM" fehldiagnostiziert.

## Ledger (`docs/MATCHING.md`)
Eine Zeile pro Adresse, Duplikate verboten, Größe ≠ 0:
`| va (seg:off) | name | size | status | note |` mit Status ∈ `MATCH | RELOCS | PENDING`.
Notiz-Format für verifizierte Zeilen (von `tools/verify.py` gelesen):
`src=<quelldatei>; flags="<cflags>"; <freitext>` — verify baut die Kombination
einmal neu und vergleicht dann jede zugehörige Zeile (kein Vertrauen auf
vorhandene OBJs). PENDING-Zeilen tragen kein `src=` und werden nicht gebaut.

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

## Offen (Phase 0 abgeschlossen — Restpunkte)
1. Overlay-Inhalt (≈141 KB) über die Laderoutinen klären
2. LINK.EXE (DOSX16) haengt unter dosbox-x in allen DPMI-Varianten (HDPMI32,
   HDPMI16, intern) — fuer `gen_link_stubs.py`/`build_replacement` (Phase 6)
   wird ein nativer OMF-Linker gebraucht (Kandidat: jwlink/wlink) oder eine
   andere Emulator-Konfiguration

## Regeln aus der Praxis (bei jedem Bau beachten)
- **Quelldateien 8.3-konform** benennen: MSC-CL (1992) oeffnet keine
  Langdateinamen und stirbt sonst LAUTLOS (cget.c vs. calib_get.c).
- OMF-Objekte von MSC7 tragen Fixups als **kompakte 0x9C-Records** (nach
  COMENT class 0xA2), nicht als klassisches FIXUPP 0xF4 — omfdump.py kann beide.
- PUBDEF-Eintraege von MSC7 haben ein Typindex-Byte (0x00) hinter dem Offset.
- **GitHub-Push (Sandbox):** git-HTTPS faellt an schannel (SEC_E_NO_CREDENTIALS),
  Credential-Helper und sh-Prompt-Skripte sterben an der msys-Signalpipe.
  Einmal-Push mit Token-URL: `$tok = gh auth token; git -c credential.helper=
  push https://mogeldev:$tok@github.com/....git master` (Remote-URL danach
  neutral zuruecksetzen, Token nie persistieren).

## Fremdcode (Phase 1, getrennt führen)
MS-C-CRT (Nachweis: Runtime-Banner in der Binary) als Bibliothek markieren und **nicht** decompilieren, sobald die CRT-Region per Kalibrier-Kompilierung abgesteckt ist.

## Phase-0-Evidenz (ScanIdioms-Lauf, 2026-11-23, 68 452 Instruktionen)

**CPU-Basis: 80186/80286 — kein 386.** `PUSHA` 17, `POPA` 13, `ENTER` 600, `LEAVE` 1315,
`IMUL` (reg-Form) 100, `INSB/OUTSB` vorhanden; `0x66`-Präfix nur 8× (Rauschen/Daten),
`0x67` = 0. → Kalibrier-Kandidat **`/G1`** (80186); `/G2` nur, falls ein echtes
286-Idiom auftaucht.

**Memory-Modell: MEDIUM `/AM`** (korrigiert 2026-11-23 durch Kalibrierung):
Getter-Familie 35ca:8090..9c liest Globals near (`mov ax,[disp16]`, DGROUP-relativ,
Fixup-maskiert) und returnt `retf` → **near-Daten + far-Code = Medium**.
Die fruehere large/huge-Vermutung war falsch; DGROUP ist vermutlich `0x58FC` + 64 KiB
(bis Paragraph `0x68FC`), der Rest bis `0x71E7` sind FAR-Daten-Segmente.
Bildlayout (Paragraphen): Code `0–0x52B1`, Stack `0x52B1–0x58FC` (`SS:SP=52B1:1000`),
DGROUP-Daten `0x58FC–0x68FC`, FAR-Daten `0x68FC–0x71E7`.

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
