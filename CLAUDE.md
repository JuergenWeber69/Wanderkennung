# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Python pipeline that turns a registered point cloud of a building floor (E57/LAS) into a closed DXF wall-axis drawing (with wall thickness) for import into BricsCAD. The full development plan — architecture, library choices, phase-by-phase spec with effort estimates, and known risks — is in `docs/entwicklungsplan.html` (German). Read it before implementing any phase; this CLAUDE.md only summarizes structure and conventions.

The project is organized as **13 phases (P0–P13)**, each independently testable, executed roughly in order (P11 calibration runs in parallel with P5–P9). Phase 0 (target accuracy, see `docs/phase0_testdaten.md`), Phase 1 (project setup), Phase 2 (`io_utils/reader.py`, `preprocessing/denoise.py`), Phase 3 (`preprocessing/slicing.py`), Phase 4 (`geometry/normals.py`), Phase 5 (`geometry/plane_segmentation.py`), and Phase 6 (`geometry/wall_classification.py`) are complete. Phases 5-6's thresholds are only validated against clean synthetic data so far — the plan flags Phase 5 as the one requiring the most recalibration against real scans (Phase 11).

Deviation from the plan doc's example code for `ist_wandkandidat`: the plan hardcodes the vertical-angle tolerance as `80 <= winkel_zur_z <= 100`; the implementation instead takes `normal_threshold_deg` as a parameter (`(90 - normal_threshold_deg) <= winkel_zur_z <= (90 + normal_threshold_deg)`) so it stays driven by `config/parameter_default.yaml`'s `normal_threshold_deg` rather than a second hardcoded constant. Remaining processing modules are stubs (`raise NotImplementedError`) to be filled in phase by phase per the plan. Note: the plan's own module tree (§4 of `docs/entwicklungsplan.html`) names the I/O package `io/` — the actual code deviates to `io_utils/` for the reason below.

## Commands

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python pipeline.py <eingabe> <config.yaml> <ausgabe.ply> [<z_min> <z_max>]
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

- `pipeline.py` — orchestrates phases 2-6 for a single floor (read → denoise/downsample → optional height slice → normals → RANSAC plane segmentation → wall classification), then writes a checkpoint PLY (wall candidates in red, other detected planes in gray) instead of a DXF — Phase 7-10 aren't implemented yet, so there's no fragment clustering, axis computation, corner closing, or DXF export. This checkpoint output is exactly the "visual inspection after each phase" practice the plan calls for; once Phase 7-10 land, `run()` extends past wall classification and the final output switches to real DXF via `io_utils/writer_dxf.py`.
- `batch_runner.py` — reads a `Name;Hoehe` floor list (same format as the existing LISP tool `PWSCHNITT-BATCH`) and runs `pipeline` per floor, writing one DXF per floor. This is the integration point with the existing BricsCAD/LISP workflow (Phase 12).
- `config/parameter_default.yaml` — all tunable thresholds (RANSAC distance, angle tolerances, cluster radius, wall thickness bounds, etc.). **Never hardcode these values in module code** — the plan explicitly calls out per-scanner/per-building-type recalibration (Phase 11) as a first-class requirement, so thresholds must stay in per-project YAML files named `config/parameter_<projekttyp>.yaml`.
- I/O lives in `io_utils/`, not `io/` — a top-level package named `io` cannot be imported at all on Python 3.11+ (`io` is a frozen stdlib module and always wins over a same-named package on `sys.path`), so don't rename it back.

## Conventions

- Code identifiers and comments in this repo mix German domain terms (e.g. `wandkandidat`, `gruppiere_fragmente`, `schliesse_ecken`) matching the plan's vocabulary — keep new functions consistent with that naming rather than translating to English.
- Each phase's expected effort and acceptance bar is documented in the plan; when implementing a phase, visually verify intermediate results (matplotlib / `open3d.visualization`) as described there rather than trusting numeric output alone — this is called out as essential for calibration-heavy phases (P5, P7, P8, P9).
- DXF output uses layer `WAND_ACHSEN` (configurable via `dxf_layer_wandachsen`), matching the existing LISP tool `PWWAND-SNAP` layer convention.
