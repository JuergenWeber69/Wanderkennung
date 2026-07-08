# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Python pipeline that turns a registered point cloud of a building floor (E57/LAS) into a closed DXF wall-axis drawing (with wall thickness) for import into BricsCAD. The full development plan — architecture, library choices, phase-by-phase spec with effort estimates, and known risks — is in `docs/entwicklungsplan.html` (German). Read it before implementing any phase; this CLAUDE.md only summarizes structure and conventions.

The project is organized as **13 phases (P0–P13)**, each independently testable, executed roughly in order (P11 calibration runs in parallel with P5–P9). Phase 0 (target accuracy, see `docs/phase0_testdaten.md`), Phase 1 (project setup), Phase 2 (`io_utils/reader.py`, `preprocessing/denoise.py`), Phase 3 (`preprocessing/slicing.py`), Phase 4 (`geometry/normals.py`), and Phase 5 (`geometry/plane_segmentation.py`) are complete. Phase 5's thresholds (`epsilon_plane`, `min_points_plane`) are only validated against clean synthetic data so far — the plan flags this as the phase requiring the most recalibration against real scans (Phase 11). Remaining processing modules are stubs (`raise NotImplementedError`) to be filled in phase by phase per the plan. Note: the plan's own module tree (§4 of `docs/entwicklungsplan.html`) names the I/O package `io/` — the actual code deviates to `io_utils/` for the reason below.

## Commands

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python pipeline.py <eingabe> <config.yaml> <ausgabe.dxf>
python batch_runner.py <eingabe> <geschosse.csv> <config.yaml> <ausgabe_verzeichnis>
```

No test runner or linter is configured yet. Tests belong in `tests/test_<modul>.py` per module, but the suite doesn't exist yet — set up a framework (pytest is the natural choice given the dependency stack) before adding the first test.

## Architecture

Processing chain, each phase feeding the next (see `docs/entwicklungsplan.html` §2 for the full diagram):

```
Rohpunktwolke → io_utils/reader.py → preprocessing/denoise.py → preprocessing/slicing.py
  → geometry/normals.py → geometry/plane_segmentation.py (RANSAC)
  → geometry/wall_classification.py → geometry/fragment_clustering.py (DBSCAN)
  → geometry/wall_pairing.py → geometry/polygon_closing.py (shapely)
  → io_utils/writer_dxf.py (ezdxf)
```

- `pipeline.py` — orchestrates all phases for a single floor; loads a YAML config and will wire the modules together as they're implemented.
- `batch_runner.py` — reads a `Name;Hoehe` floor list (same format as the existing LISP tool `PWSCHNITT-BATCH`) and runs `pipeline` per floor, writing one DXF per floor. This is the integration point with the existing BricsCAD/LISP workflow (Phase 12).
- `config/parameter_default.yaml` — all tunable thresholds (RANSAC distance, angle tolerances, cluster radius, wall thickness bounds, etc.). **Never hardcode these values in module code** — the plan explicitly calls out per-scanner/per-building-type recalibration (Phase 11) as a first-class requirement, so thresholds must stay in per-project YAML files named `config/parameter_<projekttyp>.yaml`.
- I/O lives in `io_utils/`, not `io/` — a top-level package named `io` cannot be imported at all on Python 3.11+ (`io` is a frozen stdlib module and always wins over a same-named package on `sys.path`), so don't rename it back.

## Conventions

- Code identifiers and comments in this repo mix German domain terms (e.g. `wandkandidat`, `gruppiere_fragmente`, `schliesse_ecken`) matching the plan's vocabulary — keep new functions consistent with that naming rather than translating to English.
- Each phase's expected effort and acceptance bar is documented in the plan; when implementing a phase, visually verify intermediate results (matplotlib / `open3d.visualization`) as described there rather than trusting numeric output alone — this is called out as essential for calibration-heavy phases (P5, P7, P8, P9).
- DXF output uses layer `WAND_ACHSEN` (configurable via `dxf_layer_wandachsen`), matching the existing LISP tool `PWWAND-SNAP` layer convention.
