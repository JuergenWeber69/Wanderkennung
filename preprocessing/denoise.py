"""Phase 2: SOR-Ausreißerfilter und Voxel-Downsampling."""


def denoise_and_downsample(pcd, sor_nb_neighbors, sor_std_ratio, voxel_size):
    pcd, _ = pcd.remove_statistical_outlier(
        nb_neighbors=sor_nb_neighbors, std_ratio=sor_std_ratio
    )
    pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return pcd
