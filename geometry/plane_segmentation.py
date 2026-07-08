"""Phase 5: Iteratives RANSAC zur Ebenensegmentierung (Kernstück der Pipeline)."""


def segment_planes(pcd, distance_threshold, min_points, max_planes=60):
    ebenen = []
    rest = pcd
    for _ in range(max_planes):
        if len(rest.points) < min_points:
            break
        modell, inliers = rest.segment_plane(
            distance_threshold=distance_threshold, ransac_n=3, num_iterations=2000
        )
        if len(inliers) < min_points:
            break
        ebene = rest.select_by_index(inliers)
        ebenen.append((modell, ebene))
        rest = rest.select_by_index(inliers, invert=True)
    return ebenen, rest
