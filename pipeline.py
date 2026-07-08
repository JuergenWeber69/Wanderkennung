"""Orchestrierung aller Phasen: Rohpunktwolke -> geschlossenes Wandachsen-DXF.

Verdrahtung der Einzelschritte folgt, sobald die jeweiligen Phasen
(Phase 2-10, siehe Entwicklungsplan) implementiert sind.
"""

import yaml


def load_config(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(eingabe_pfad, config_pfad, ausgabe_pfad):
    config = load_config(config_pfad)
    raise NotImplementedError


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python pipeline.py <eingabe> <config.yaml> <ausgabe.dxf>")
        sys.exit(1)

    run(sys.argv[1], sys.argv[2], sys.argv[3])
