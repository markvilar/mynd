"""Module for batch registration."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeAlias, TypeVar

import tqdm

from mynd.geometry import PointCloud, PointCloudLoader

from .data_types import RegistrationResult
from .pipeline import RegistrationPipeline, apply_registration_pipeline
from .utilities import RegistrationIndex


Key: TypeVar = TypeVar("Key")


@dataclass(frozen=True)
class RegistrationBatch(Generic[Key]):
    """Class representing a registration batch."""

    @dataclass(frozen=True)
    class PairResult:
        """Class representing a registration result."""

        target: Key
        source: Key
        result: RegistrationResult

    @dataclass
    class Result:
        """Class representing a batch registration result."""

        target: Key
        sources: dict[Key, RegistrationResult]

    loaders: dict[Key, PointCloudLoader] = field(default_factory=dict)

    def keys(self) -> list[Key]:
        """Returns the keys in the registration batch."""
        return self.loaders.keys()

    def get(self, key: Key) -> PointCloudLoader | None:
        """Returns the point cloud loader or none."""
        return self.loaders.get(key)


Batch: TypeAlias = RegistrationBatch
Pipeline: TypeAlias = RegistrationPipeline
Index: TypeAlias = RegistrationIndex


Callback: TypeAlias = Callable[[Key, Key, RegistrationResult], None]


def register_batch(
    batch: Batch,
    pipeline: Pipeline,
    indices: list[Index],
    callback: Callback | None = None,
) -> list[Batch.PairResult]:
    """Registers a batch of point clouds with the given pipeline."""

    results: list[Batch.PairResult] = list()
    for index in tqdm.tqdm(indices, desc="registering batch..."):

        target_loader: PointCloudLoader = batch.get(index.target)
        target_cloud: PointCloud = target_loader().unwrap()

        source_loader: PointCloudLoader = batch.get(index.source)
        source_cloud: PointCloud = source_loader().unwrap()

        result: RegistrationResult = apply_registration_pipeline(
            pipeline,
            target=target_cloud,
            source=source_cloud,
        )

        if callback is not None:
            callback(index.target, index.source, result)

        pairwise: Batch.PairResult = Batch.PairResult(
            target=index.target, source=index.source, result=result
        )

        results.append(pairwise)

    return results
