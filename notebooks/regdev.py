import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(r"""### Prepare point cloud loaders""")
    return


@app.cell
def __():
    from pathlib import Path

    from mynd.geometry import PointCloud, PointCloudLoader
    from mynd.io import read_point_cloud, create_point_cloud_loader

    DATA_DIR: Path = Path("/home/martin/dev/mynd/.cache")

    point_cloud_files: dict = {
        0: DATA_DIR / Path("qdc5ghs3_20100430_024508.ply"),
        1: DATA_DIR / Path("qdc5ghs3_20120501_033336.ply"),
        2: DATA_DIR / Path("qdc5ghs3_20130405_103429.ply"),
        3: DATA_DIR / Path("qdc5ghs3_20210315_230947.ply"),
    }

    loaders: dict[int, PointCloudLoader] = {
        key: create_point_cloud_loader(path)
        for key, path in point_cloud_files.items()
        if path.exists()
    }
    return (
        DATA_DIR,
        Path,
        PointCloud,
        PointCloudLoader,
        create_point_cloud_loader,
        loaders,
        point_cloud_files,
        read_point_cloud,
    )


@app.cell
def __(Path, PointCloud, RegistrationResult, loaders):
    import open3d.utility as utils

    from mynd.io import read_config
    from mynd.utils.log import logger

    from mynd.registration import (
        PointCloudProcessor,
        GlobalRegistrator,
        IncrementalRegistrator,
    )

    from mynd.registration import (
        build_point_cloud_processor,
        build_ransac_registrator,
        build_regular_icp_registrator,
        build_colored_icp_registrator,
    )

    from mynd.registration import log_registration_result

    CONFIG_FILE: Path = Path(
        "/home/martin/dev/mynd/config/registration_simple.toml"
    )

    preprocessor: PointCloudProcessor = build_point_cloud_processor(
        {
            "downsample": {"spacing": 0.20},
            "estimate_normals": {"radius": 0.40, "neighbours": 30},
        }
    )

    ransac_registrator: GlobalRegistrator = build_ransac_registrator(
        {
            "feature": {"radius": 2.00, "neighbours": 200},
            "estimator": {"with_scaling": True},
            "validators": {
                "distance_threshold": 0.15,
                "edge_threshold": 0.95,
                "normal_threshold": 5.0,
            },
            "convergence": {"max_iteration": 10000000, "confidence": 1.0},
            "algorithm": {
                "distance_threshold": 0.15,
                "sample_count": 3,
                "mutual_filter": True,
            },
        }
    )

    regular_icp: IncrementalRegistrator = build_regular_icp_registrator(
        {
            "huber_kernel": {"k": 0.40},
            "convergence_criteria": {
                "relative_fitness": 1e-6,
                "relative_rmse": 1e-6,
                "max_iteration": 50,
            },
            "distance_threshold": 0.50,
        }
    )

    colored_icp: IncrementalRegistrator = build_colored_icp_registrator(
        {
            "colored_icp_estimation": {"lambda_geometric": 0.968},
            "huber_kernel": {"k": 0.40},
            "convergence_criteria": {
                "relative_fitness": 1e-6,
                "relative_rmse": 1e-6,
                "max_iteration": 50,
            },
            "distance_threshold": 0.50,
        }
    )

    source: PointCloud = loaders.get(0)().unwrap()
    target: PointCloud = loaders.get(1)().unwrap()

    source_pre: PointCloud = preprocessor(source)
    target_pre: PointCloud = preprocessor(target)

    result: RegistrationResult = ransac_registrator(
        target=target_pre, source=source_pre
    )

    logger.info("----------- RANSAC -----------")
    log_registration_result(result=result, target=target_pre, source=source_pre)
    logger.info("------------------------------")

    result: RegistrationResult = colored_icp(
        source=source_pre,
        target=target_pre,
        transformation=result.transformation,
    )

    logger.info("--------- REGULAR ICP ---------")
    log_registration_result(result=result, target=target_pre, source=source_pre)
    logger.info("-------------------------------")

    result: RegistrationResult = regular_icp(
        source=source_pre,
        target=target_pre,
        transformation=result.transformation,
    )

    logger.info("--------- COLORED ICP ---------")
    log_registration_result(result=result, target=target_pre, source=source_pre)
    logger.info("-------------------------------")
    return (
        CONFIG_FILE,
        GlobalRegistrator,
        IncrementalRegistrator,
        PointCloudProcessor,
        build_colored_icp_registrator,
        build_point_cloud_processor,
        build_ransac_registrator,
        build_regular_icp_registrator,
        colored_icp,
        log_registration_result,
        logger,
        preprocessor,
        ransac_registrator,
        read_config,
        regular_icp,
        result,
        source,
        source_pre,
        target,
        target_pre,
        utils,
    )


if __name__ == "__main__":
    app.run()
