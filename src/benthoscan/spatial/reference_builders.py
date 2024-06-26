"""TODO"""

import polars as pl

from loguru import logger
from result import Ok, Err, Result

from benthoscan.spatial import (
    Vec3,
    Identifier,
    Geolocation,
    Orientation,
    SpatialReference,
)


IDENTIFIER_KEY = "identifier"
GEOLOCATION_KEY = "geolocation"
ORIENTATION_KEY = "orientation"
GEOLOCATION_ACCURACY_KEY = "geolocation_accuracy"
ORIENTATION_ACCURACY_KEY = "orientation_accuracy"


def map_dataframe_columns_to_references(
    dataframe: pl.DataFrame, attribute_to_column: dict[str, str]
) -> list[SpatialReference]:
    """TODO"""

    identifier_keys: dict[str, str] = attribute_to_column[IDENTIFIER_KEY]
    geolocation_keys: dict[str, str] = attribute_to_column[GEOLOCATION_KEY]
    orientation_keys: dict[str, str] = attribute_to_column[ORIENTATION_KEY]

    # TODO: Add functionality to read accuracies from data frame

    references: list[SpatialReference] = list()
    for row in dataframe.iter_rows(named=True):

        identifier: dict[str, str] = {
            attr: row.get(col)
            for attr, col in attribute_to_column[IDENTIFIER_KEY].items()
        }

        geolocation: dict[str, float] = {
            attr: row.get(col)
            for attr, col in attribute_to_column[GEOLOCATION_KEY].items()
        }

        orientation: dict[str, float] = {
            attr: row.get(col)
            for attr, col in attribute_to_column[ORIENTATION_KEY].items()
        }

        references.append(
            SpatialReference(
                identifier=Identifier(**identifier),
                geolocation=Geolocation(**geolocation),
                orientation=Orientation(**orientation),
            )
        )

    return references


def add_constants_to_references(
    references: list[SpatialReference], constants: dict
) -> list[SpatialReference]:
    """Adds constant values to the references."""

    has_geolocation_accuracy_constant: bool = GEOLOCATION_ACCURACY_KEY in constants
    has_orientation_accuracy_constant: bool = GEOLOCATION_ACCURACY_KEY in constants

    for reference in references:
        if not reference.has_geolocation_accuracy and has_geolocation_accuracy_constant:
            reference.geolocation_accuracy: Vec3 = Vec3(
                *constants[GEOLOCATION_ACCURACY_KEY]
            )

        if not reference.has_orientation_accuracy and has_orientation_accuracy_constant:
            reference.orientation_accuracy: Vec3 = Vec3(
                *constants[ORIENTATION_ACCURACY_KEY]
            )

    return references


def build_references_from_dataframe(
    dataframe: pl.DataFrame,
    column_maps: dict,
    constants: dict,
) -> Result[list[SpatialReference], str]:
    """Builds references from a dataframe by mapping column values to attributes,
    and adding constant values."""

    for required_map in [IDENTIFIER_KEY, GEOLOCATION_KEY, ORIENTATION_KEY]:
        if not required_map in column_maps:
            return Err(f"reference configuration missing map: {required_map}")

    references: list[SpatialReference] = map_dataframe_columns_to_references(
        dataframe, column_maps
    )

    references: list[SpatialReference] = add_constants_to_references(
        references, constants
    )

    return Ok(references)
