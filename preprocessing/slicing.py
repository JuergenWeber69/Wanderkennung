"""Phase 3: Geschosszuschnitt per Höhenband, analog zu PWSCHNITT-BATCH (Name;Hoehe)."""

import numpy as np


def slice_by_height(pcd, z_min, z_max):
    pts = np.asarray(pcd.points)
    mask = (pts[:, 2] >= z_min) & (pts[:, 2] <= z_max)
    return pcd.select_by_index(np.where(mask)[0])
