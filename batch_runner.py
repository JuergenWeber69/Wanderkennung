"""Phase 12: Stapelverarbeitung über eine Geschossliste (Name;Hoehe), analog PWSCHNITT-BATCH.

Liest pro Zeile ein Geschoss, führt es durch pipeline.run() und legt
ein DXF pro Geschoss im Ausgabeverzeichnis ab.
"""

import csv


def lade_geschossliste(pfad):
    geschosse = []
    with open(pfad, "r", encoding="utf-8") as f:
        for name, hoehe in csv.reader(f, delimiter=";"):
            geschosse.append((name, float(hoehe)))
    return geschosse


def run_batch(eingabe_pfad, geschossliste_pfad, config_pfad, ausgabe_verzeichnis):
    raise NotImplementedError


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print("Usage: python batch_runner.py <eingabe> <geschosse.csv> <config.yaml> <ausgabe_verzeichnis>")
        sys.exit(1)

    run_batch(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
