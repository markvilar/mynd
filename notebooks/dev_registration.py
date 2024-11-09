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

    from mynd.registration import MultiTargetIndex, generate_cascade_indices
    from mynd.registration import (
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

    from mynd.registration import Pipeline


    @dataclass
    class RegistrationConfig:
        \"\"\"Class representing a registration configuration.\"\"\"

        @dataclass
        class Module:
            \"\"\"Class representing a config item.\"\"\"

            preprocessors: list[dict]
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
        incrementors: list[RegistrationConfig.Module] = [
            RegistrationConfig.Module(**item) for item in config.get(\"incrementors\")
        ]
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
    initializer = build_feature_registrator(config.initializer.registrator).unwrap()

    logger.info(initializer)

    # TODO: Build incremental registrators
    # registrator: IncrementalRegistrator = build_icp_registrator(
    #    module_config[\"registrator\"],
    # ).unwrap()

    # build_point_cloud_processor(
    #    model[\"method\"], model[\"parameters\"]
    # ).unwrap()
    """,
    name="__",
)


@app.cell
def __(
    PointCloud,
    RegistrationResult,
    apply_registration_modules,
    loaders,
    log_registration,
    modules,
):
    from typing import Optional

    source: int = 0
    target: int = 3

    source_cloud: PointCloud = loaders[source]().unwrap()
    target_cloud: PointCloud = loaders[target]().unwrap()

    module_results: list[RegistrationResult] = list()
    current_result: Optional[RegistrationResult] = None

    def on_result(
        source: PointCloud, target: PointCloud, result: RegistrationResult
    ) -> None:
        """Callback that is executed for every pair-wise registration."""
        log_registration(source=0, target=3, result=result)

    results: dict[int, RegistrationResult] = apply_registration_modules(
        modules=modules,
        source=source_cloud,
        target=target_cloud,
        callback=on_result,
    )
    return (
        Optional,
        current_result,
        module_results,
        on_result,
        results,
        source,
        source_cloud,
        target,
        target_cloud,
    )


@app.cell
def __(
    PointCloud,
    copy,
    downsample_point_cloud,
    np,
    source_cloud,
    target_cloud,
    vis,
):
    def visualize_plotly(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
        source_color: list = None,
        target_color: list = None,
        title: str = "",
        window_width: int = 1024,
        window_height: int = 768,
    ) -> None:
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)

        if source_color:
            source_temp.paint_uniform_color(source_color)
        if target_color:
            target_temp.paint_uniform_color(target_color)

        source_temp.transform(transformation)

        vis.draw_plotly(
            geometry_list=[source_temp, target_temp],
            window_name=title,
            width=window_width,
            height=window_height,
        )

    visualize: bool = True

    source_down: PointCloud = downsample_point_cloud(
        cloud=source_cloud, spacing=0.10
    )
    target_down: PointCloud = downsample_point_cloud(
        cloud=target_cloud, spacing=0.10
    )
    return source_down, target_down, visualize, visualize_plotly


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Plot registration results
        """
    )
    return


@app.cell
def __(
    PointCloud,
    create_subplots,
    loaders,
    test_results,
    test_source,
    test_target,
    trace_registration_result,
    visualize_registration,
):
    import plotly.express as px
    import plotly.graph_objects as go

    figure: go.Figure = create_subplots(rows=2, cols=3)
    colors: list[str] = px.colors.sequential.Plasma_r * 2
    for index, (result, color) in enumerate(zip(test_results, colors)):
        traces: dict[str, go.Trace] = trace_registration_result(
            result, name=f'Regi. {index}', legendgroup=index, color=color
        )
        figure.add_trace(traces['fitness'], row=1, col=1)
        figure.add_trace(traces['rmse'], row=1, col=2)
        figure.add_trace(traces['correspondences'], row=1, col=3)
        figure.add_trace(traces['scale'], row=2, col=1)
        figure.add_trace(traces['rotation'], row=2, col=2)
        figure.add_trace(traces['translation'], row=2, col=3)
    figure.update_layout(
        height=800, width=1000, title_text='Registration Results'
    )
    figure.show()
    visualize_test: bool = False
    if visualize_test:
        source_cloud_1: PointCloud = loaders[test_source]().unwrap()
        target_cloud_1: PointCloud = loaders[test_target]().unwrap()
        for index, result in enumerate(test_results):
            visualize_registration(
                source=source_cloud_1,
                target=target_cloud_1,
                transformation=result.transformation,
                title=f'Test case: {test_source}, {test_target}, {index}',
            )
    return (
        color,
        colors,
        figure,
        go,
        index,
        px,
        result,
        source_cloud_1,
        target_cloud_1,
        traces,
        visualize_test,
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Generate indices and perform registration
        """
    )
    return


@app.cell
def __(MultiTargetIndex, generate_cascade_indices, loaders):
    indices: list[MultiTargetIndex] = generate_cascade_indices(len(loaders))

    result_storage = {
        "feature_matching": dict(),
        "incremental_coarse": dict(),
    }
    return indices, result_storage


@app.cell
def __(
    RegistrationResult,
    indices,
    loaders,
    log_registration,
    preprocessor,
    registration_worker,
    registrator,
    result_storage,
):
    for index_1 in indices:
        source_1 = index_1.source
        results_1: dict[int, RegistrationResult] = dict()
        for target_1 in index_1.targets:
            result_1: RegistrationResult = registration_worker(
                source_loader=loaders[source_1],
                target_loader=loaders[target_1],
                preprocessor=preprocessor,
                registrator=registrator,
            )
            log_registration(source_1, target_1, result_1)
            results_1[target_1] = result_1
        result_storage['feature_matching'][source_1] = results_1
    return index_1, result_1, results_1, source_1, target_1


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Draw registration and plot results
        - TODO: Draw registered point clouds
        - TODO: Plot point clouds, correspondences, and error distribution
        """
    )
    return


@app.cell
def __(PointCloud, loaders, result_storage, visualize_registration):
    visualize_global_results: bool = False
    if visualize_global_results:
        for source_2, registrations in result_storage[
            'feature_matching'
        ].items():
            source_cloud_2: PointCloud = loaders[source_2]().unwrap()
            for target_2, result_2 in registrations.items():
                target_cloud_2: PointCloud = loaders[target_2]().unwrap()
                visualize_registration(
                    source=source_cloud_2,
                    target=target_cloud_2,
                    transformation=result_2.transformation,
                    title=f'Registration - source: {source_2}, target: {target_2}',
                )
    return (
        registrations,
        result_2,
        source_2,
        source_cloud_2,
        target_2,
        target_cloud_2,
        visualize_global_results,
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Perform multiway registration
        """
    )
    return


@app.cell
def __(build_pose_graph, optimize_pose_graph, reg, result_storage, util):
    initial_graph: reg.PoseGraph = build_pose_graph(
        result_storage["incremental_coarse"]
    )

    with util.VerbosityContextManager(util.VerbosityLevel.Debug) as cm:
        optimized_graph: reg.PoseGraph = optimize_pose_graph(
            initial_graph,
            correspondence_distance=0.075,
            prune_threshold=0.25,
            preference_loop_closure=1.0,
            reference_node=0,
        )
    return cm, initial_graph, optimized_graph


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Draw final registration results
        """
    )
    return


@app.cell
def __(PointCloud, loaders, optimized_graph, result_storage, vis):
    transformed_clouds: list[PointCloud] = list()

    for identifier in result_storage["incremental_coarse"]:

        cloud: PointCloud = loaders[identifier]().unwrap()
        cloud.transform(optimized_graph.nodes[identifier].pose)
        transformed_clouds.append(cloud)

    vis.draw_geometries(transformed_clouds)
    return cloud, identifier, transformed_clouds


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
