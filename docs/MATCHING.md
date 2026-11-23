# MATCHING-Ledger

Eine Zeile pro Adresse; Größe = echte Länge ≠ 0; Status `MATCH | RELOCS | PENDING`.
Zähler immer aus dieser Datei neu rechnen, nie aus dem Gedächtnis (Vorlage Phase 5).
Notiz-Konvention: `obj=<Pfad>` verweist auf das OMF-Objekt für verify.py.

| va | name | size | status | note |
|----|------|------|--------|------|
| 35ca:8090 | get0 | 4 | RELOCS | obj=build/cget.OBJ, disp16-DGROUP-Fixup; src/calib/cget.c /G1 /AM /Gs /Os |
| 35ca:8094 | get1 | 4 | RELOCS | obj=build/cget.OBJ, disp16-DGROUP-Fixup; src/calib/cget.c /G1 /AM /Gs /Os |
| 35ca:8098 | get2 | 4 | RELOCS | obj=build/cget.OBJ, disp16-DGROUP-Fixup; src/calib/cget.c /G1 /AM /Gs /Os |
| 35ca:809c | get3 | 4 | RELOCS | obj=build/cget.OBJ, disp16-DGROUP-Fixup; src/calib/cget.c /G1 /AM /Gs /Os |
| 1fd5:0006 | get_1a4 | 4 | RELOCS | obj=build/cget2.OBJ, disp16-Fixup (DGROUP 0x1A4); src/calib/cget2.c |
| 43a0:000c | get_2fce | 4 | RELOCS | obj=build/cget2.OBJ, disp16-Fixup (DGROUP 0x2FCE); src/calib/cget2.c |
| 4dce:0002 | get_2c50 | 4 | RELOCS | obj=build/cget2.OBJ, disp16-Fixup (DGROUP 0x2C50); src/calib/cget2.c |
| 4e99:000c | get_2d0c | 4 | RELOCS | obj=build/cget2.OBJ, disp16-Fixup (DGROUP 0x2D0C); src/calib/cget2.c |
| 257f:0004 | get_l | 8 | RELOCS | obj=build/cget3.OBJ, 2x disp16-Fixup (DGROUP 0x13D2, DX:AX-Rueckgabe); Ghidra FUN_1871_d0e4 |
| 398d:0004 | get_ln | 8 | RELOCS | obj=build/cget3.OBJ, __near, 2x disp16-Fixup (DGROUP 0x14C4); Ghidra FUN_35ca_3c34 |
| 2131:000c | set_flag | 6 | RELOCS | obj=build/cflag1.OBJ, disp16-Fixup (DGROUP 0x0F44), imm8 0x40; src/calib/cflag1.c |
| 20b2:0000 | OR_JOIN | 14 | RELOCS | obj=build/cor1.OBJ, disp16-Fixup (DGROUP 0x6DE); `void: g_or \|= x` (Original schreibt zurueck: 09 statt 0B). Inventarfenster 18 B laeuft in Folge-Getter -> `--size 14` |
| 20ab:000c | _wait_change | 20 | RELOCS | obj=build/cor1.OBJ, 2x disp16-Fixup (DGROUP 0x6DA); Spin-Wait auf `volatile int` (Reload im Schleifenkopf, `74 F8` exakt) |
| 4fac:000a | inc_39f8_capped | 12 | RELOCS | obj=build/cinc1.OBJ, 2x disp16-Fixup (DGROUP 0x39F8); if (g<0x10) g++; |
| 458e:a20e | SLOT_FILL | 166 | PENDING | Slotfuellroutine (pascal, 1 Far-Param, 8 Felder 0/2/4/9/11/13/15/19, conv+update-Calls). 4 Hypothesen: v3 (162/166 B!) fehlen nur die Stack-Rueckschreibungen des gewanderten Pointers; Original haelt si rein im Register + es aus [bp+8]. Form komplett dokumentiert (ENTER 2, or/jge, e9-Branch, imul 0x27, [bx+disp]-Stores) |
| 4fad:0006 | CONV | 16 | PENDING | Lookup table[c] (Wort-Tabelle DGROUP 0x396A, near-pascal). 5 Quellformen + /Od-/O1-/O2 getestet: /Os liefert ALLES identisch (55 8b ec-Rahmen, [bp+4], Lookup, retn 2) bis auf 2 Bytes: d1 e3 (shl) statt 03 db (add bx,bx). Slot-Subsystem (4fab/4fac/4fad/458e_a20e) zeigt konsistent Hand-ASM-Idiome |
| 4fab:000a | get_39f8_clamped | 16 | PENDING | Aufrufer FUN_458e_a20e beweist Semantik: Slot-Index-Allokator (Zaehler DGROUP 0x39F8, max 16, Slotgr. 0x27, Sentinel -1 wird geprueft via `if (-1 < iVar1)`). Sprung-Merge-Form (jl/B8FFFF/EB03/A1/C3) aus keinem MSC7-C-Konstrukt erzeugbar (5 Kombis getestet) — Hand-/Inline-ASM bleibt Hauptverdacht |
