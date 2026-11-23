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
