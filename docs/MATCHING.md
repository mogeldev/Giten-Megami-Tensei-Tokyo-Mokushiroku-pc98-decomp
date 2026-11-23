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
