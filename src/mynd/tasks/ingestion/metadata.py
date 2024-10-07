"""Module for ingesting camera metadata into a mynd backend."""

from collections.abc import Mapping

import polars as pl

from ...camera import Metadata


def map_metadata_to_cameras(
    metadata: pl.DataFrame,
    label_column: str,
    data_columns: list[str],
) -> Mapping[str, Metadata]:
    """Creates a mapping from camera label to metadata fields from a table."""

    assert (
        label_column in metadata
    ), f"missing camera label column: {label_column}"

    found_data_columns: list[str] = [
        column for column in data_columns if column in metadata
    ]

    camera_metadata: dict[str, Metadata] = {
        row.get(label_column): {
            column: row.get(column) for column in found_data_columns
        }
        for row in metadata.iter_rows(named=True)
    }

    return camera_metadata
