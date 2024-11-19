"""Module for registration CLI entrypoints."""

from pathlib import Path

from mynd.backend import metashape
from mynd.collections import GroupID
from mynd.geometry import PointCloudLoader
from mynd.io import read_config

from mynd.registration import RegistrationBatch
from mynd.registration import RegistrationPipeline, build_registration_pipeline
from mynd.registration import (
    RegistrationIndex,
    generate_indices_cascade,
    generate_indices_one_way,
)

from mynd.tasks.registration import register_groups

from mynd.utils.log import logger
from mynd.utils.result import Result


def invoke_registration(
    project: Path,
    destination: Path,
    config_file: Path,
    cache: Path,
    reference: str | None = None,
    visualize: bool = False,
    force_export: bool = False,
) -> None:
    """Invokes a registration task - Prepares point cloud loaders, selects a reference,
    builds registration batch and pipeline."""

    metashape.load_project(project).unwrap()

    point_cloud_loaders: dict[GroupID, PointCloudLoader] = (
        retrieve_point_clouds(cache)
    )
    reference_group: GroupID = select_registration_reference(
        reference, point_cloud_loaders
    )

    config: dict = read_config(config_file).unwrap()

    pipeline: RegistrationPipeline = build_registration_pipeline(
        config.get("registration")
    )
    batch: RegistrationBatch = RegistrationBatch[GroupID](point_cloud_loaders)

    INDEX_STRATEGY: str = "one-way"

    match INDEX_STRATEGY:
        case "one-way":
            indices: list[RegistrationIndex] = generate_indices_one_way(
                reference_group, batch.keys()
            )
        case "cascade":
            indices: list[RegistrationIndex] = generate_indices_cascade(
                batch.keys()
            )
        case _:
            raise NotImplementedError

    batch_result: RegistrationBatch.Result = register_groups(
        batch, indices, pipeline, reference=reference_group, visualize=visualize
    ).unwrap()

    metashape.apply_registration_results(
        batch_result.target, batch_result.sources
    )

    metashape.save_project(destination).unwrap()


def retrieve_point_clouds(cache: Path) -> dict[GroupID, PointCloudLoader]:
    """Prepares registration groups by retrieving"""

    retrieval_result: Result = (
        metashape.dense_services.retrieve_dense_point_clouds(
            cache=cache,
            overwrite=True,
        )
    )
    loaders: dict[GroupID, PointCloudLoader] = retrieval_result.unwrap()
    return loaders


def select_registration_reference(
    reference_label: str, loaders: dict[GroupID, PointCloudLoader]
) -> GroupID:
    """Gets a registration reference from the given loaders."""

    groups: dict[str, GroupID] = {group.label: group for group in loaders}

    if reference_label not in groups:
        logger.error(f"missing reference label: {reference_label}")
        exit()

    reference_group: GroupID = groups.get(reference_label)

    return reference_group
