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
    name="__"
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
        logger.error(f"invalid number of point clouds for registration: {count}")
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
        ### Logging Helpers
        """
    )
    return


@app.cell
def __(decompose_transformation, logger):
    from mynd.registration import RegistrationResult


    def log_registration(
        source: int, target: int, result: RegistrationResult
    ) -> None:
        """TODO"""

        scale, rotation, translation = decompose_transformation(
            result.transformation
        )

        logger.info("")
        logger.info(f"Source:       {source}")
        logger.info(f"Target:       {target}")
        logger.info(f"Corresp.:     {len(result.correspondence_set)}")
        logger.info(f"Fitness:      {result.fitness}")
        logger.info(f"Inlier RMSE:  {result.inlier_rmse}")
        logger.info(f"Trans. scale:    {scale}")
        logger.info(f"Trans. trans.:   {translation}")
        logger.info(f"Trans. rot.:     {rotation}")
        logger.info("")
    return RegistrationResult, log_registration


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
        PointCloudProcessor,
        GlobalRegistrator,
        IncrementalRegistrator,
    )

    # Builders
        build_point_cloud_processor,
        build_feature_registrator,
        build_icp_registrator,
    )

    from mynd.registration import RegistrationPipeline, apply_registration_pipeline


    @dataclass
    class RegistrationConfig:
        \"\"\"Class representing a registration configuration.\"\"\"

        @dataclass
        class Module:
            \"\"\"Class representing a config item.\"\"\"

            preprocessor: list[dict]
            registrator: dict

        initializer: Module
        incrementors: list[Module]


    def create_registration_config(config: dict) -> RegistrationConfig:
        \"\"\"Creates a registration pipeline config.\"\"\"
        # TODO: Get initializer modules
        initializer: RegistrationConfig.Module = RegistrationConfig.Module(
            **config.get(\"initializer\")
        )
        # TODO: Get incrementor modules
        if \"incrementors\" in config:
            incrementors: list[RegistrationConfig.Module] = [
                RegistrationConfig.Module(**item)
                for item in config.get(\"incrementors\")
            ]
        else:
            incrementors: list = list()
        return RegistrationConfig(initializer, incrementors)


    CONFIG_FILE: Path = Path(
        \"/home/martin/dev/mynd/config/registration_simple.toml\"
    )
    config: dict = read_config(CONFIG_FILE).unwrap()

    config: RegistrationConfig = create_registration_config(
        config.get(\"registration\")
    )

    logger.info(\"---------- Registration ----------\")
    logger.info(f\" - Initializer: {config.initializer}\")
    logger.info(f\" - Incrementors: {config.incrementors}\")
    logger.info(\"----------------------------------\")


    # TODO: Build global registrator
    initializer: RegistrationPipeline.InitializerModule = (
        RegistrationPipeline.InitializerModule(
            preprocessor=build_point_cloud_processor(
                **config.initializer.preprocessor
            ),
            registrator=build_feature_registrator(
                config.initializer.registrator
            ).unwrap(),
        )
    )

    pipeline: RegistrationPipeline = RegistrationPipeline(initializer)

    target: PointCloud = loaders.get(0)().unwrap()
    source: PointCloud = loaders.get(1)().unwrap()

    result: RegistrationResult = apply_registration_pipeline(
        pipeline, source=source, target=target
    )

    logger.info(result)

    # result: RegistrationResult = initializer.registrator(target=target_pre, source=source_pre)
    # apply_registration_pipeline

    # TODO: Build incremental registrators
    # registrator: IncrementalRegistrator = build_icp_registrator(
    #    module_config[\"registrator\"],
    # ).unwrap()

    # build_point_cloud_processor(
    #    model[\"method\"], model[\"parameters\"]
    # ).unwrap()
    """,
    name="__"
)


@app.cell
def __():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
