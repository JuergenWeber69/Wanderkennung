"""Phase 4: Normalenschätzung und konsistente Ausrichtung."""

import numpy as np
import open3d as o3d


def estimate_normals(pcd, search_radius, max_nn, orient_k):
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=search_radius, max_nn=max_nn
        )
    )

    # orient_normals_consistent_tangent_plane trianguliert intern per qhull;
    # bei absoluten Vermessungskoordinaten (UTM/Gauss-Krueger, Millionenbereich)
    # stoesst qhull dabei an die Fliesskomma-Praezisionsgrenze ("wide merge"-
    # Fehler). Deshalb fuer die Ausrichtung um den Schwerpunkt zentrieren und
    # danach zuruecktranslieren, damit die Weltkoordinaten erhalten bleiben.
    punkte = np.asarray(pcd.points)
    schwerpunkt = punkte.mean(axis=0)
    pcd.points = o3d.utility.Vector3dVector(punkte - schwerpunkt)
    pcd.orient_normals_consistent_tangent_plane(k=orient_k)
    pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points) + schwerpunkt)

    return pcd
