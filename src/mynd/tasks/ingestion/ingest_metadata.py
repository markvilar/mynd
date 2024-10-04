"""Module for ingesting camera metadata into a mynd backend."""

from collections.abc import Mapping

import polars as pl

from ...utils.log import logger


def map_metadata_to_cameras(
    metadata: pl.DataFrame,
    label_column: str,
    data_columns: list[str],
) -> Mapping[str, dict]:
    """Creates a mapping from camera label to metadata fields from a table."""

    required_columns: list[str] = [label_column] + data_columns

    has_column: dict[str, bool] = {
        column: column in metadata.columns for column in required_columns
    }

    for column, valid in has_column.items():
        if not valid:
            logger.error(f"column not in metadata: {column}")
            return

    camera_metadata: dict[str, dict] = {
        row.get(label_column): {column: row.get(column) for column in data_columns}
        for row in metadata.iter_rows(named=True)
    }

    return camera_metadata
