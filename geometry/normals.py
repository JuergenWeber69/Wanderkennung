"""Phase 4: Normalenschätzung und konsistente Ausrichtung."""

import open3d as o3d


def estimate_normals(pcd, search_radius, max_nn, orient_k):
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=search_radius, max_nn=max_nn
        )
    )
    pcd.orient_normals_consistent_tangent_plane(k=orient_k)
    return pcd
