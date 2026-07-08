"""Phase 2: E57/LAS-Einlesen mit Chunking, Umwandlung in einheitliches Open3D-Punktformat."""

from pathlib import Path

import numpy as np
import open3d as o3d

# Punkte pro Chunk beim LAS-Streaming, damit große Dateien nicht komplett in
# den Speicher geladen werden müssen (siehe Entwicklungsplan Phase 2).
LAS_CHUNK_SIZE = 5_000_000


def read_point_cloud(pfad, chunk_size=LAS_CHUNK_SIZE):
    """Liest E57/LAS/LAZ sowie die von Open3D nativ unterstützten Formate
    (PLY/PCD/XYZ) und liefert eine einheitliche open3d.geometry.PointCloud.
    """
    pfad = Path(pfad)
    suffix = pfad.suffix.lower()

    if suffix in (".las", ".laz"):
        return _read_las(pfad, chunk_size)
    if suffix == ".e57":
        return _read_e57(pfad)
    return o3d.io.read_point_cloud(str(pfad))


def _read_las(pfad, chunk_size):
    import laspy

    teilwolken = []
    with laspy.open(str(pfad)) as reader:
        for chunk in reader.chunk_iterator(chunk_size):
            punkte = np.column_stack((chunk.x, chunk.y, chunk.z))
            teil = o3d.geometry.PointCloud()
            teil.points = o3d.utility.Vector3dVector(punkte)
            teilwolken.append(teil)

    return _merge(teilwolken)


def _read_e57(pfad):
    import pye57

    e57 = pye57.E57(str(pfad))
    teilwolken = []
    for scan_index in range(e57.scan_count):
        daten = e57.read_scan(scan_index, ignore_missing_fields=True)
        punkte = np.column_stack(
            (daten["cartesianX"], daten["cartesianY"], daten["cartesianZ"])
        )
        teil = o3d.geometry.PointCloud()
        teil.points = o3d.utility.Vector3dVector(punkte)
        teilwolken.append(teil)

    return _merge(teilwolken)


def _merge(teilwolken):
    if not teilwolken:
        return o3d.geometry.PointCloud()

    pcd = teilwolken[0]
    for teil in teilwolken[1:]:
        pcd += teil
    return pcd
