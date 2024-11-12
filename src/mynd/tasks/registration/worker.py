"""Module for executing registration tasks."""

from collections.abc import Callable

from mynd.collections import GroupID
from mynd.geometry import PointCloud, PointCloudLoader

from mynd.registration import RegistrationPipeline, RegistrationResult
from mynd.registration import RegistrationBatch, register_batch
from mynd.registration import RegistrationIndex

from mynd.visualization import visualize_registration

from mynd.utils.log import logger
from mynd.utils.result import Ok, Result


def register_groups(
    batch: RegistrationBatch,
    indices: list[RegistrationIndex],
    pipeline: RegistrationPipeline,
    reference: GroupID,
    visualize: bool = False,
    callback: Callable | None = None,
) -> Result[RegistrationBatch.Result, str]:
    """Registers a batch of groups with the given"""

    logger.info("")
    logger.info("Performing batch registration...")
    registration_results: list[RegistrationBatch.PairResult] = register_batch(
        batch,
        pipeline,
        indices,
        callback=callback,
    )
    logger.info("Batch registration done!")
    logger.info("")

    if visualize:
        for registration in registration_results:
            target_loader: PointCloudLoader = batch.get(registration.target)
            source_loader: PointCloudLoader = batch.get(registration.source)

            target_cloud: PointCloud = target_loader().unwrap()
            source_cloud: PointCloud = source_loader().unwrap()

            visualize_registration(
                target=target_cloud,
                source=source_cloud,
                transformation=registration.result.transformation,
                title=f"{registration.source.label}",
            )

    batch_result: RegistrationBatch.Result = reference_registration_results(
        target=reference, pairwise_result=registration_results
    )

    return Ok(batch_result)


def reference_registration_results(
    target: GroupID, pairwise_result: list[RegistrationBatch.PairResult]
) -> RegistrationBatch.Result:
    """Reference a collection of registration results to a target."""

    source_results: dict[GroupID, RegistrationResult] = dict()

    for pairwise in pairwise_result:
        if pairwise.target == target:
            source_results[pairwise.source] = pairwise.result

    return RegistrationBatch.Result(target=target, sources=source_results)
