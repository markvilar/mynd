"""Module for ingesting camera metadata into a mynd backend."""

import polars as pl

from mynd.camera import Camera
from mynd.collections import GroupID
from mynd.utils.result import Err, Result

from mynd.backend import metashape


def map_metadata_to_cameras(
    metadata: pl.DataFrame,
    label_column: str,
    data_columns: list[str],
) -> dict[str, Camera.Metadata]:
    """Creates a mapping from camera label to metadata fields from a table."""

    assert (
        label_column in metadata
    ), f"missing camera label column: {label_column}"

    found_data_columns: list[str] = [
        column for column in data_columns if column in metadata
    ]

    camera_metadata: dict[str, Camera.Metadata] = {
        row.get(label_column): {
            column: row.get(column) for column in found_data_columns
        }
        for row in metadata.iter_rows(named=True)
    }

    return camera_metadata


def ingest_metadata_locally(
    metadata: pl.DataFrame,
    config: dict,
    target: str,
) -> Result[None, str]:
    """Ingest camera metadata via API. If no target group is given, the backend
    will try to target any group."""

    METADATA_CONFIG_KEY: str = "metadata"
    TABLE_MAP_CONFIG_KEY: str = "table_maps"

    if METADATA_CONFIG_KEY not in config:
        return Err(f"missing config entry: {METADATA_CONFIG_KEY}")

    metadata_config: dict = config.get("metadata")

    if TABLE_MAP_CONFIG_KEY not in metadata_config:
        return Err(f"missing metadata config entry: {TABLE_MAP_CONFIG_KEY}")

    table_maps: dict = metadata_config.get("table_maps")

    camera_metadata: dict[str, dict] = map_metadata_to_cameras(
        metadata,
        table_maps.get("label_field"),
        table_maps.get("data_fields"),
    )

    group_identifiers: list[GroupID] = (
        metashape.get_group_identifiers().unwrap()
    )
    group_map: dict[str, GroupID] = {
        identifier.label: identifier for identifier in group_identifiers
    }

    if target not in group_map:
        return Err("did not find target group: {target}")

    target_group: GroupID = group_map.get(target)

    update_result: Result = metashape.camera_services.update_camera_metadata(
        target_group, camera_metadata
    )

    return update_result
