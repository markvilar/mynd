"""Module for reconstruction task workers."""

from pathlib import Path
from typing import Callable

from result import Ok, Err, Result

from benthoscan.utils.log import logger
from benthoscan.utils.progress_bar import percent_bar

from .processor_builders import build_sparse_processor, build_dense_processor
from .config_types import ReconstructionConfig


def log_reconstruction_task(config: ReconstructionConfig) -> None:
    """TODO"""

    logger.info("")
    logger.info(f"---------- RECONSTRUCTION TASK ----------")
    logger.info(f" - Document: {Path(config.document.path).stem}")

    for label in config.target_labels:
        logger.info(f" - Target: {label}")

    for entry in config.processors["sparse"]:
        process: str = entry["process"]
        enabled: bool = entry["enabled"]
        parameters: dict = entry["parameters"]

        logger.info(f" - Sparse: {process}, {enabled}")

    for entry in config.processors["dense"]:
        process: str = entry["process"]
        enabled: bool = entry["enabled"]
        parameters: dict = entry["parameters"]

        logger.info(f" - Dense: {process}, {enabled}")

    logger.info(f"-----------------------------------------")
    logger.info("")


def build_processors(configs: list[dict], builder: Callable) -> list[Result]:
    """TODO"""
    results: list = list()
    for config in configs:
        if not config["enabled"]:
            continue
        results.append(builder(config))

    return results


def execute_reconstruction_task(config: ReconstructionConfig) -> Result[None, str]:
    """TODO"""

    log_reconstruction_task(config)

    sparse_build_results: list[Result] = build_processors(
        config.processors["sparse"], build_sparse_processor
    )

    dense_build_results: list[Result] = build_processors(
        config.processors["dense"],
        build_dense_processor,
    )

    # TODO: Handle errors when processing the build results
    sparse_processors: list = [result.unwrap() for result in sparse_build_results]
    dense_processors: list = [result.unwrap() for result in dense_build_results]

    # TODO: Calculate some statistics to improve logging
    step_count: int = len(sparse_processors) + len(dense_processors)

    # Set up a dedicated logger for the processors since the backend calls exceeds logurus stack
    # call depth
    processor_logger = logger.opt(depth=-1)

    # TODO: Add signal handler

    for chunk in config.document.chunks:
        if not chunk.enabled:
            logger.warning(f"chunk {chunk.label} is not enabled")
            continue

        # NOTE: Apply dense processors
        for processor in sparse_processors:
            result: Result[None, str] = processor(
                chunk, progress_fun=percent_bar.update
            )

            match result:
                case Err(error):
                    logger.error(f"sparse processing error: {error}")
                    return Err(error)

        # NOTE: Apply dense processors
        for processor in dense_processors:
            result: Result[None, str] = processor(
                chunk, progress_fun=percent_bar.update
            )

            match result:
                case Err(error):
                    logger.error(f"dense processing error: {error}")
                    return Err(error)

    return Ok(None)
