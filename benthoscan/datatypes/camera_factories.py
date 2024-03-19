"""Module with factories for various camera types."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import DataTable, TableFieldMap
from benthoscan.datatypes.geometry import Vec3

from .camera_types import (
    Camera,
    Cameras,
    CameraFactory,
    CameraAssembly,
    CameraAssemblyFactory,
)


CAMERA_MAP_GROUPS = [
    "labels",
    "position",
    "position_accuracy",
    "orientation",
    "orientation_accuracy",
]


@dataclass
class LabelsMap:
    items: List[TableFieldMap]


@dataclass
class PositionMap:
    items: List[TableFieldMap]


@dataclass
class OrientationMap:
    items: List[TableFieldMap]


@dataclass
class PositionAccuracyMap:
    items: List[TableFieldMap]


@dataclass
class OrientationAccuracyMap:
    items: List[TableFieldMap]


@dataclass
class CameraTableMap:
    """Data class representing how tables are parsed into cameras."""

    # Members
    labels: LabelsMap
    position: Optional[PositionMap] = None
    orientation: Optional[OrientationMap] = None

    # TODO: Implement data class for position and orientation accuracy
    position_accuracy: Optional[PositionAccuracyMap] = None
    orientation_accuracy: Optional[OrientationAccuracyMap] = None

    def has_position(self) -> bool:
        """Returns true if the fields has position."""
        return not self.position is None

    def has_position_accuracy(self) -> bool:
        """Returns true if the fields has position accuracies."""
        return not self.position_accuracy is None

    def has_orientation(self) -> bool:
        """Returns true if the fields has position."""
        return not self.orientation is None

    def has_orientation_accuracy(self) -> bool:
        """Returns true if the fields has position accuracies."""
        return not self.orientation_accuracy is None


def create_camera_table_map(maps: Dict[str, List]) -> Result[CameraTableMap, str]:
    """Creates a parser that interpretes a collection of table columns as the
    fields of a camera."""

    field_maps = dict()

    attributes = {key: None for key in CAMERA_MAP_GROUPS}

    map_types = {
        "labels": LabelsMap,
        "position": PositionMap,
        "orientation": OrientationMap,
        "position_accuracy": PositionAccuracyMap,
        "orientation_accuracy": OrientationAccuracyMap,
    }

    # Distribute field maps into map groups
    for key in CAMERA_MAP_GROUPS:
        if key in maps:
            map_type = map_types[key]
            attributes[key] = map_type(
                [TableFieldMap(**fieldmap) for fieldmap in maps[key]]
            )

    return Ok(CameraTableMap(**attributes))


CameraTableMaps = Dict[str, CameraTableMap]


def create_camera_table_maps(config: Dict) -> Result[CameraTableMaps, str]:
    """Creates mappings from table columns to camera attributes."""
    camera_maps = dict()
    for key in config:
        result: Result[CameraTableMap, str] = create_camera_table_map(
            config[key]["maps"]
        )

        if result.is_err():
            return result

        camera_maps[key] = result.unwrap()

    return Ok(camera_maps)


TableRow = Dict[str, str | int | float]


def map_columns_to_dict(row: TableRow, component_map: LabelsMap) -> Dict[str, str]:
    """Maps columns in a table row to a dictionary."""
    fields = {map.name: row[map.column] for map in component_map.items}
    return dict(**fields)


def map_columns_to_vec3(row: TableRow, component_map: PositionMap) -> Vec3:
    """Maps columns in a table row to a Vec3 type."""
    fields = {map.name: row[map.column] for map in component_map.items}
    return Vec3(**fields)


def map_table_row_to_camera(row: TableRow, camera_map: CameraTableMap) -> Camera:
    """Maps columns in a table row to camera."""

    label_fields: Dict[str, str] = map_columns_to_dict(row, camera_map.labels)

    reference_fields = {
        "position": None,
        "orientation": None,
        "position_accuracy": None,
        "orientation_accuracy": None,
    }

    if camera_map.position:
        reference_fields["position"]: Vec3 = map_columns_to_vec3(
            row, camera_map.position
        )

    if camera_map.orientation:
        reference_fields["orientation"]: Vec3 = map_columns_to_vec3(
            row, camera_map.orientation
        )

    if camera_map.position_accuracy:
        reference_fields["position_accuracy"]: Vec3 = map_columns_to_vec3(
            row, camera_map.position_accuracy
        )

    if camera_map.orientation_accuracy:
        reference_fields["orientation_accuracy"]: Vec3 = map_columns_to_vec3(
            row, camera_map.orientation_accuracy
        )

    labels = Camera.Labels(**label_fields)
    reference = Camera.Reference(**reference_fields)

    return Camera(labels=labels, reference=reference)


CameraGroup: TypeAlias = Dict[str, Camera]


def create_camera_groups_from_table(
    table: DataTable,
    table_maps: Dict[str, CameraTableMap],
) -> List[CameraGroup]:
    """Creates groups of cameras for each row in a table."""
    camera_groups = list()
    for index in table:
        row = table[index]

        camera_group = dict()
        for key in table_maps:
            camera = map_table_row_to_camera(row, table_maps[key])

            # Assign group to camera and add camera to group
            camera.group = key
            camera_group[key] = camera

        camera_groups.append(camera_group)

    return camera_groups


def create_assemblies_from_table(
    table: DataTable,
    camera_config: Dict,
    assembly_config: Dict,
) -> List[CameraAssembly]:
    """Creates cameras for each row in a data table."""

    table_maps = create_camera_table_maps(camera_config).unwrap()

    camera_groups: List[CameraGroup] = create_camera_groups_from_table(
        table,
        table_maps,
    )

    # Get group keys from assembly config
    master_key: str = assembly_config["master"]
    slave_keys: List[str] = assembly_config["slaves"]

    # Assembly cameras
    assemblies = list()
    for cameras in camera_groups:
        master = cameras[master_key]
        slaves = [cameras[key] for key in slave_keys]

        assembly = CameraAssembly(
            master=master,
            slaves=slaves,
        )

        assemblies.append(assembly)

    return assemblies
