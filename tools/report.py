#!/usr/bin/env python3
"""report.py — erzeugt docs/STATUS.md aus Ledger + coverage (Vorlage Phase 6).

Zaehler werden nie aus dem Gedaechtnis geschrieben: Ledger ist die Quelle fuer
MATCH/RELOCS/PENDING, coverage.compute() fuer die Byte-Metrik. Der handgeschriebene
Teil von STATUS.md (Offene Punkte, Toolchain-Notizen) steht zwischen den Markern
MANUAL-BEGIN/MANUAL-END und bleibt unangetastet."""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys

sys.path.insert(0, os.path.join(ROOT, "tools"))
import coverage  # noqa: E402

STATUS = os.path.join(ROOT, "docs", "STATUS.md")


def keep_manual(path):
    if not os.path.isfile(path):
        return ""
    text = open(path, encoding="utf-8").read()
    if "<!-- MANUAL-BEGIN -->" not in text:
        return ""
    manual = text.split("<!-- MANUAL-BEGIN -->", 1)[1]
    manual = manual.split("<!-- MANUAL-END -->", 1)[0]
    return manual.strip("\n")


def main():
    s = coverage.compute()
    today = datetime.date.today().isoformat()
    pct = f"{100 * s['ok_b'] / s['eig_b']:.3f}%" if s["eig_b"] else "-"

    lines = [
        "# STATUS",
        "",
        f"<!-- GENERIERT von tools/report.py am {today} — Zahlen nicht von Hand -->",
        "<!-- Handgeschriebener Teil zwischen MANUAL-BEGIN und MANUAL-END bleibt erhalten. -->",
        "",
        "## Ledger (Quelle: docs/MATCHING.md)",
        "",
        "| Status | Anzahl |",
        "|---|---|",
        f"| MATCH | {s['n_match']} |",
        f"| RELOCS | **{s['n_relocs']}** |",
        f"| PENDING | **{s['n_pending']}** |",
        "",
        "PENDING-Faelle (Details in `docs/MATCHING.md`, Idiome in `docs/IDIOMS.md`):",
        "",
    ]
    pend = [(v[0], v[1], v[2], v[4]) for v in s["ledger"].values() if v[3] == "PENDING"]
    if not pend:
        lines.append("_(keine)_")
    for va, name, size, note in pend:
        short = note.split(";")[0][:150]
        lines.append(f"- `{va}` **{name}** ({size} B) — {short}")
    lines += [
        "",
        "## Coverage (ehrliche Byte-Metrik)",
        "",
        "| Kategorie | Wert |",
        "|---|---|",
        f"| Inventar-Einträge | **{s['tot_f']}** Code-Funktionen + **{s['n_data']}** Daten |",
        f"| Daten (belegt, `not_code.csv`) | {s['nc_b']} B |",
        f"| Code-Bytes | {s['tot_b']} |",
        f"| − Fremd-CRT (Signaturen) | {s['fremd_b']} |",
        f"| = **Eigencode-Bytes** | **{s['eig_b']}** |",
        f"| davon **verifiziert** | **{s['ok_b']} ({pct})** |",
        f"| PENDING-Bytes | {s['pend_b']} |",
        "",
        f"Code-Funktionen: **{s['tot_f']}**, davon verifiziert **{s['ok_f']}**.",
        "",
        "## Regionen (64 KiB)",
        "",
        "| Region | Funktionen | ok | Code-B | verifiziert | CRT | Daten | PENDING |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for reg in sorted(s["regions"]):
        d = s["regions"][reg]
        eig = d["total"] - d["fremd"]
        rp = f"{100 * d['matched'] / eig:.1f}%" if eig > 0 else "-"
        lines.append(f"| {reg:#06x} | {d['n']} | {d['nm']} | {d['total']} | "
                     f"{d['matched']} ({rp}) | {d['fremd']} | {d['notcode']} | {d['pend']} |")

    manual = keep_manual(STATUS)
    lines += [
        "",
        "<!-- MANUAL-BEGIN -->",
        manual if manual else DEFAULTS,
        "<!-- MANUAL-END -->",
        "",
    ]
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"STATUS.md geschrieben: {os.path.relpath(STATUS, ROOT)} "
          f"(Ledger {s['n_relocs']} RELOCS / {s['n_pending']} PENDING, "
          f"{pct} Eigenbytes verifiziert)")


DEFAULTS = """## Toolchain

- **MSC 7.0 (CL 8.00, 1992)**: dosbox-x + HDPMI32-TSR, `-nopromptfolder`,
  APPDATA-Redirect, `cycles=max` — Rezept in `docs/CONVENTIONS.md`.
- CFLAGS **bestaetigt: `/G1 /AM /Gs /Os`** (byte-identische Kalibrierfunktionen).

## Offen (Reihenfolge fuer die naechsten Runden)

1. `LINK.EXE` (DOSX16) haengt unter dosbox-x in allen DPMI-Varianten — Voraussetzung
   fuer `build_replacement` (Phase 6); Kandidat: nativer OMF-Linker (jwlink)
2. Slot-Subsystem: `__asm`-Rekonstruktion erwaege (dort ist C nachweislich erschoepft)
3. Weiter im Familien-Workflow: ALU-/DOS-Helfer mit `55 8b ec`-Rahmen"""


if __name__ == "__main__":
    main()
