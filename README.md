# Wanderkennung

Python-Pipeline zur automatisierten Wanderkennung: aus einer registrierten
Punktwolke eines Gebäudegeschosses (E57/LAS) wird automatisiert ein DXF mit
fertigen Wandachsen (inkl. Wandstärke, geschlossenes Grundrisspolygon) für
den Import in BricsCAD erzeugt.

Der vollständige Entwicklungsplan (Architektur, Phasen P0–P13, Aufwandsschätzung,
Risiken) ist in `docs/entwicklungsplan.html` dokumentiert.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Projektstruktur

```
wanderkennung/
├── config/                    # Parametersätze je Gebäudetyp/Scanner
├── io/                        # E57/LAS-Einlesen, DXF-Export
├── preprocessing/             # Rauschfilterung, Downsampling, Geschosszuschnitt
├── geometry/                  # Normalen, Ebenensegmentierung, Wandklassifizierung,
│                               # Clustering, Wandpaarung, Eckenschluss
├── pipeline.py                # Orchestrierung aller Phasen für ein Geschoss
├── batch_runner.py            # Stapelverarbeitung über eine Geschossliste
└── tests/                     # Unit-Tests je Modul
```

## Status

Projekt-Setup (Phase 1) abgeschlossen. Die Verarbeitungsmodule sind als
Gerüst angelegt und werden Phase für Phase implementiert (siehe Entwicklungsplan).
