import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(r"""### Configure directories and load project""")
    return


@app.cell
def __():
    from pathlib import Path

    from mynd.backend import metashape as metashape
    from mynd.utils.result import Ok, Err, Result

    CACHE: Path = Path("/data/kingston_snv_01/acfr_point_clouds")
    INPUT_DIR: Path = Path("/data/kingston_snv_01/acfr_metashape_projects_dev")
    OUTPUT_DIR: Path = Path(
        "/data/kingston_snv_01/acfr_metashape_projects_registered"
    )

    # NOTE: Change to dense project
    INPUT_PROJECT: Path = INPUT_DIR / "r234xgje_dense_with_metadata.psz"
    DESTINATION_PROJECT: Path = (
        OUTPUT_DIR / "r234xgje_registered_with_metadata.psz"
    )

    assert CACHE.exists(), f"directory does not exist: {CACHE}"
    assert OUTPUT_DIR.exists(), f"directory does not exist: {OUTPUT_DIR}"
    assert INPUT_PROJECT.exists(), f"project does not exist: {INPUT_PROJECT}"

    match metashape.load_project(INPUT_PROJECT):
        case Ok(path):
            pass
        case Err(error_message):
            pass
        case _:
            raise NotImplementedError
    return (
        CACHE,
        DESTINATION_PROJECT,
        Err,
        INPUT_DIR,
        INPUT_PROJECT,
        OUTPUT_DIR,
        Ok,
        Path,
        Result,
        error_message,
        metashape,
        path,
    )


@app.cell
def __(mo):
    mo.md(r"""### Create preprocessors and registrators""")
    return


@app.cell
def __(Path):
    from collections.abc import Callable
    from typing import TypeAlias

    import open3d.utility as utils

    from mynd.io import read_config

    from mynd.geometry import PointCloudProcessor

    from mynd.registration import (
        RegistrationPipeline,
        apply_registration_pipeline,
        build_registration_pipeline,
    )

    from mynd.utils.log import logger

    CONFIG_FILE: Path = Path(
        "/home/martin/dev/mynd/config/registration_simple.toml"
    )

    config: dict = read_config(CONFIG_FILE).unwrap()

    for key, parameters in config.get("registration").items():
        print(f"Key: {key} - parameters: {parameters}")

    pipeline: RegistrationPipeline = build_registration_pipeline(
        config.get("registration")
    )
    return (
        CONFIG_FILE,
        Callable,
        PointCloudProcessor,
        RegistrationPipeline,
        TypeAlias,
        apply_registration_pipeline,
        build_registration_pipeline,
        config,
        key,
        logger,
        parameters,
        pipeline,
        read_config,
        utils,
    )


@app.cell
def __(mo):
    mo.md(r"""### Retrieve dense point clouds and run pipeline""")
    return


@app.cell
def __(
    CACHE,
    Result,
    apply_registration_pipeline,
    logger,
    metashape,
    pipeline,
):
    from dataclasses import dataclass

    from mynd.collections import GroupID
    from mynd.geometry import PointCloud, PointCloudLoader
    from mynd.registration import RegistrationResult
    from mynd.registration import log_registration_result

    def callback_registration(
        source: PointCloud, target: PointCloud, result: RegistrationResult
    ) -> None:
        """Callback for registration."""
        print(f"Target: {target}")
        print(f"Source: {source}")
        print(f"Result: fitness: {result.fitness}")
        print(f"Result, rmse.:   {result.inlier_rmse}")
        print(f"Result, corre.:  {len(result.correspondence_set)}")
        print(f"Result, trans.:  {result.transformation}")

    @dataclass(frozen=True)
    class PointCloudHandle:
        """Class representing a point cloud handle."""

        group: GroupID
        loader: PointCloudLoader

    # Retrieve dense point clouds
    retrieval_result: Result = (
        metashape.dense_services.retrieve_dense_point_clouds(
            cache=CACHE, overwrite=False
        )
    )

    if retrieval_result.is_err():
        logger.error(retrieval_result.err())

    point_cloud_loaders: dict[GroupID, PointCloudLoader] = retrieval_result.ok()

    handles: list[PointCloudHandle] = [
        PointCloudHandle(id, loader)
        for id, loader in point_cloud_loaders.items()
    ]

    target: PointCloud = handles[0].loader().unwrap()
    source: PointCloud = handles[1].loader().unwrap()

    print(target)
    print(source)

    print("Running registration pipeline")
    result: RegistrationResult = apply_registration_pipeline(
        pipeline, target=target, source=source, callback=callback_registration
    )
    return (
        GroupID,
        PointCloud,
        PointCloudHandle,
        PointCloudLoader,
        RegistrationResult,
        callback_registration,
        dataclass,
        handles,
        log_registration_result,
        point_cloud_loaders,
        result,
        retrieval_result,
        source,
        target,
    )


if __name__ == "__main__":
    app.run()
