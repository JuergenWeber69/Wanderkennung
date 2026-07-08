"""Phase 6: Filterung von Ebenen zu Wandkandidaten (Vertikalität, Höhe, Flächengröße)."""

import numpy as np


def ist_wandkandidat(modell, ebene, min_hoehe, min_breite, normal_threshold_deg):
    normale = np.array(modell[:3])
    winkel_zur_z = np.degrees(np.arccos(abs(normale[2])))
    bbox = ebene.get_axis_aligned_bounding_box()
    hoehe = bbox.get_extent()[2]
    breite = max(bbox.get_extent()[0], bbox.get_extent()[1])
    return (
        (90 - normal_threshold_deg) <= winkel_zur_z <= (90 + normal_threshold_deg)
        and hoehe >= min_hoehe
        and breite >= min_breite
    )
