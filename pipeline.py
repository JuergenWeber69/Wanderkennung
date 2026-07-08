"""Orchestrierung aller Phasen: Rohpunktwolke -> geschlossenes Wandachsen-DXF.

Solange Phase 7-10 (Fragment-Clustering, Wandpaarung, Eckenschluss, DXF-Export)
noch nicht implementiert sind, endet der Durchlauf nach der Wand-Klassifizierung
(Phase 6) und schreibt die erkannten Wandkandidaten als eingefärbte PLY-Datei --
der im Entwicklungsplan empfohlene Praxistest-Checkpoint nach Phase 6.
"""

import yaml
import open3d as o3d

from io_utils.reader import read_point_cloud
from preprocessing.denoise import denoise_and_downsample
from preprocessing.slicing import slice_by_height
from geometry.normals import estimate_normals
from geometry.plane_segmentation import segment_planes
from geometry.wall_classification import ist_wandkandidat

WAND_FARBE = [0.8, 0.1, 0.1]
SONSTIGE_FARBE = [0.6, 0.6, 0.6]


def load_config(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(eingabe_pfad, config_pfad, ausgabe_pfad, z_min=None, z_max=None):
    cfg = load_config(config_pfad)

    pcd = read_point_cloud(eingabe_pfad)
    print(f"Eingelesen: {len(pcd.points)} Punkte")

    pcd = denoise_and_downsample(
        pcd, cfg["sor_nb_neighbors"], cfg["sor_std_ratio"], cfg["voxel_size"]
    )
    print(f"Nach Denoise/Downsampling: {len(pcd.points)} Punkte")

    if z_min is not None and z_max is not None:
        pcd = slice_by_height(pcd, z_min, z_max)
        print(f"Nach Geschosszuschnitt [{z_min}, {z_max}]: {len(pcd.points)} Punkte")

    pcd = estimate_normals(
        pcd, cfg["normal_search_radius"], cfg["normal_max_nn"], cfg["normal_orient_k"]
    )

    ebenen, rest = segment_planes(
        pcd, cfg["epsilon_plane"], cfg["min_points_plane"], cfg["max_planes"]
    )
    print(f"Ebenen gefunden: {len(ebenen)}, Restpunkte: {len(rest.points)}")

    wandkandidaten = [
        (modell, ebene)
        for modell, ebene in ebenen
        if ist_wandkandidat(
            modell,
            ebene,
            cfg["wand_min_hoehe"],
            cfg["wand_min_breite"],
            cfg["normal_threshold_deg"],
        )
    ]
    print(f"Wandkandidaten: {len(wandkandidaten)} von {len(ebenen)} Ebenen")

    _schreibe_checkpoint_ply(ebenen, wandkandidaten, ausgabe_pfad)
    return wandkandidaten


def _schreibe_checkpoint_ply(alle_ebenen, wandkandidaten, ausgabe_pfad):
    wand_ids = {id(ebene) for _, ebene in wandkandidaten}

    teilwolken = []
    for _, ebene in alle_ebenen:
        teil = o3d.geometry.PointCloud(ebene)
        farbe = WAND_FARBE if id(ebene) in wand_ids else SONSTIGE_FARBE
        teil.paint_uniform_color(farbe)
        teilwolken.append(teil)

    if not teilwolken:
        return

    gesamt = teilwolken[0]
    for teil in teilwolken[1:]:
        gesamt += teil

    o3d.io.write_point_cloud(ausgabe_pfad, gesamt)
    print(f"Checkpoint-PLY geschrieben (Wandkandidaten rot, übrige Ebenen grau): {ausgabe_pfad}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) not in (4, 6):
        print(
            "Usage: python pipeline.py <eingabe> <config.yaml> <ausgabe.ply> "
            "[<z_min> <z_max>]"
        )
        sys.exit(1)

    z_min = float(sys.argv[4]) if len(sys.argv) == 6 else None
    z_max = float(sys.argv[5]) if len(sys.argv) == 6 else None
    run(sys.argv[1], sys.argv[2], sys.argv[3], z_min=z_min, z_max=z_max)
