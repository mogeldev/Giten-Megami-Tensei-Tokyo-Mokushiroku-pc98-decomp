#!/usr/bin/env python3
"""build.py — Build-Skript (Vorlage Phase 2).

ZUSTAND: MSC-8-Toolchain noch nicht kalibriert (Phase 0 offen) -> definierter
Abbruch. Kapselt spaeter: DOSBox-Aufruf + pro-Quelldatei-CFLAGS (ueberschreibbar),
isoliertes Objektverzeichnis, Basisadress-Experimente (--base), *.stamp-Cache.
Nichts wird gefaked: ohne kalibrierte Toolchain gibt es kein Build-Ergebnis."""
import sys

sys.exit("TOOLCHAIN_NOT_CALIBRATED: MSC-8-Toolchain fehlt noch (Phase 0). "
         "build.py verweigert bewusst jedes Ergebnis, bis Kalibrier-Kompilate "
         "gegen die Binary MATCHen (Vorlage Phase 0).")
