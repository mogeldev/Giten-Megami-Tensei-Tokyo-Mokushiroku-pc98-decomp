# MATCHING-Ledger

Eine Zeile pro Adresse; Größe = echte Länge ≠ 0; Status `MATCH | RELOCS | PENDING`.
Zähler immer aus dieser Datei neu rechnen, nie aus dem Gedächtnis (Vorlage Phase 5).

**Format der Notiz (von `tools/verify.py` gelesen):**
`src=<quelldatei>; flags="<cflags>"; <freitext>` — verify baut jede
(src, flags)-Kombination einmal neu und vergleicht danach alle zugehörigen
Zeilen. Damit hängt die Verifikation nicht davon ab, welches OBJ gerade in
`build/` liegt. PENDING-Zeilen tragen kein `src=` und werden nicht gebaut.

| va | name | size | status | note |
|----|------|------|--------|------|
| 35ca:8090 | get0 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16-DGROUP-Fixup |
| 35ca:8094 | get1 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16-DGROUP-Fixup |
| 35ca:8098 | get2 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16-DGROUP-Fixup |
| 35ca:809c | get3 | 4 | RELOCS | src=src/calib/cget.c; flags="/G1 /AM /Gs /Os"; disp16-DGROUP-Fixup |
| 1fd5:0006 | get_1a4 | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16-Fixup (DGROUP 0x1A4) |
| 43a0:000c | get_2fce | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16-Fixup (DGROUP 0x2FCE) |
| 4dce:0002 | get_2c50 | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16-Fixup (DGROUP 0x2C50) |
| 4e99:000c | get_2d0c | 4 | RELOCS | src=src/calib/cget2.c; flags="/G1 /AM /Gs /Os"; disp16-Fixup (DGROUP 0x2D0C) |
| 257f:0004 | get_l | 8 | RELOCS | src=src/calib/cget3.c; flags="/G1 /AM /Gs /Os"; 2x disp16-Fixup, DX:AX-Rueckgabe (Ghidra FUN_1871_d0e4) |
| 398d:0004 | get_ln | 8 | RELOCS | src=src/calib/cget3.c; flags="/G1 /AM /Gs /Os"; __near, 2x disp16-Fixup (Ghidra FUN_35ca_3c34) |
| 2131:000c | set_flag | 6 | RELOCS | src=src/calib/cflag1.c; flags="/G1 /AM /Gs /Os"; or byte [0x0F44],0x40 |
| 20b2:0000 | OR_JOIN | 14 | RELOCS | src=src/calib/cor1.c; flags="/G1 /AM /Gs /Os"; g_or \|= x (Store-Form 09, nicht Return 0B) |
| 20ab:000c | _wait_change | 20 | RELOCS | src=src/calib/cor1.c; flags="/G1 /AM /Gs /Os"; Spin-Wait auf volatile int (Reload im Loop-Kopf) |
| 4fac:000a | inc_39f8_capped | 12 | RELOCS | src=src/calib/cinc1.c; flags="/G1 /AM /Gs /Os"; if (g<0x10) g++ |
| 4fab:000a | get_39f8_clamped | 16 | PENDING | Slot-Index-Allokator (Aufrufer FUN_458e_a20e: Sentinel -1, Slots 0x27 B). Beste Variante /Ox: 14/16 B — Restdiff `C3 90` (Early-Return + Padding) vs. `EB 03` (Sprung-Merge, ein ret). Getestet: /Os, /Od, /O1, /O2, /Ox, /Os /Oy, Ternaer beide Polaritaeten, if/else+local |
| 1f2d:000e | CLAMP_A | 20 | PENDING | min(max(x,1),g), __fastcall (Arg in AX, nacktes retn), Global 0x4688. Original rahmenlos mit DX-Temp (`8B 16 d / 3B C2 / 7E 02 / 8B C2`); MSC7 liefert unter /Ox Speicher-Operanden (`39 06 d / 7D 03 / A1 d`), unter /Os einen Rahmen. 6 Varianten getestet |
| 1f2f:0002 | CLAMP_B | 20 | PENDING | Geschwister von CLAMP_A, Global 0x468A, gleiche Ursache |
| 352a:0004 | reset_9b30 | 22 | PENDING | g1=0; g2=0; far-call(0x18,1) — pascal, Callee räumt auf. MSC7: /Os|/Ot|/Ox -> `33 C0 A3 A3` (8 B, rahmenlos); /O2 -> `C7 06` x2 (12 B, mit Rahmen). Original: C7-06-Stores OHNE Rahmen -> Codegen-Generation fraglich (MSC 6.x?) |
| 4527:000a | reset_9b30b | 22 | PENDING | Duplikat-Body von reset_9b30 (zweite Code-Kopie), gleiche Ursache |
| 458e:a20e | SLOT_FILL | 166 | PENDING | Slotfuellroutine (pascal, 1 Far-Param). Beste Variante 162/166 B; Restdiff: Original wandert den Offset nur in SI (kein Zurueckschreiben des Parameters), MSC7-C schreibt Param/Stackslot zurueck |
| 4fad:0006 | CONV | 16 | PENDING | Lookup table[c] (Wort-Tabelle DGROUP 0x396A, near-pascal). /Os liefert alles identisch bis auf 2 B: `D1 E3` (shl bx,1) statt `03 DB` (add bx,bx); /Ox gegengeprueft, unveraendert |
