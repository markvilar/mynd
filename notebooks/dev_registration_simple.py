import marimo

__generated_with = "0.9.14"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Include registration modules
        """
    )
    return


app._unparsable_cell(
    r"""
    import copy

    from functools import partial
    from time import time

    from collections.abc import Callable

    import numpy as np

    import open3d
    import open3d.geometry as geom
    import open3d.pipelines.registration as reg
    import open3d.visualization as vis
    import open3d.utility as util

    from mynd.registration import (
        MultiTargetIndex,
        generate_cascade_indices,
    )

        downsample_point_cloud,
        estimate_point_cloud_normals,
    )

        register_icp,
        register_colored_icp,
        build_pose_graph,
        optimize_pose_graph,
    )

    from mynd.spatial import decompose_transformation

    from mynd.visualization import (
        visualize_registration,
        create_subplots,
        trace_registration_result,
    )

    from mynd.utils.log import logger
    from mynd.utils.result import Ok, Err, Result
    """,
    name="__",
)


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Load environment and configure data loaders
        """
    )
    return


@app.cell
def __(logger):
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

    count = len(loaders)
    if count < 2:
        logger.error(
            f"invalid number of point clouds for registration: {count}"
        )
    return (
        DATA_DIR,
        Path,
        PointCloud,
        PointCloudLoader,
        count,
        create_point_cloud_loader,
        loaders,
        point_cloud_files,
        read_point_cloud,
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Build registration modules from config
        """
    )
    return


app._unparsable_cell(
    r"""
    from dataclasses import dataclass
    from typing import TypeAlias

    from mynd.io import read_config

    # Processors and registrators
        RegistrationResult,
        PointCloudProcessor,
        GlobalRegistrator,
        IncrementalRegistrator,
    )

    # Builders
        build_point_cloud_processor,
        build_icp_registrator,
        build_ransac_registrator,
    )

    from mynd.registration import log_registration_result

    from mynd.registration import RegistrationPipeline, apply_registration_pipeline


    # TODO: Create ransac registrator
    preprocessor: PointCloudProcessor = build_point_cloud_processor(
        {
            \"downsample\": {\"spacing\": 0.20},
            \"estimate_normals\": {\"radius\": 0.40, \"neighbours\": 30},
        }
    )

    ransac_registrator: GlobalRegistrator = build_ransac_registrator(
        {
            \"feature\": {\"radius\": 2.00, \"neighbours\": 200},
            \"estimator\": {\"with_scaling\": True},
            \"validators\": {
                \"distance_threshold\": 0.15,
                \"edge_threshold\": 0.95,
                \"normal_threshold\": 5.0,
            },
            \"convergence\": {\"max_iteration\": 1000, \"confidence\": 1.0},
            \"algorithm\": {
                \"distance_threshold\": 0.15,
                \"sample_count\": 3,
                \"mutual_filter\": True,
            },
        }
    )


    logger.info(preprocessor)
    logger.info(ransac_registrator)

    # pipeline: RegistrationPipeline = RegistrationPipeline(initializer)
    # result: RegistrationResult = apply_registration_pipeline(pipeline, source=source, target=target)

    target_pre: PointCloud = preprocessor(loaders.get(0)().unwrap())
    source_pre: PointCloud = preprocessor(loaders.get(1)().unwrap())
    """,
    name="__",
)


@app.cell
def __(
    RegistrationResult,
    logger,
    open3d,
    ransac_registrator,
    source_pre,
    target_pre,
):
    with open3d.utility.VerbosityContextManager(
        open3d.utility.VerbosityLevel.Debug
    ) as cm:

        result: RegistrationResult = ransac_registrator(
            target=target_pre, source=source_pre
        )

        logger.info(result)
    return cm, result


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
