"""Module for writing camera data to ASDF files."""

import asdf
import polars as pl

from mynd.camera import Sensor, CameraCalibration, StereoRig
from mynd.collections import CameraGroup
from mynd.geometry import (
    StereoRectificationResult,
    compute_stereo_rectification,
)


def treeify_camera_group(cameras: CameraGroup) -> asdf.AsdfFile:
    """Converts a camera group to a tree."""
    tree: dict = dict()

    tree["group"] = {
        "key": cameras.group_identifier.key,
        "label": cameras.group_identifier.label,
    }

    tree["camera_attributes"] = treeify_camera_attributes(cameras.attributes)
    tree["aligned_references"] = treeify_camera_references(
        cameras.reference_estimates
    )
    tree["prior_references"] = treeify_camera_references(
        cameras.reference_priors
    )

    tree["sensors"] = [
        treeify_camera_sensor(sensor) for sensor in cameras.attributes.sensors
    ]

    tree["stereo"] = [
        treeify_stereo_rig(stereo_rig)
        for stereo_rig in cameras.attributes.stereo_rigs
    ]

    tree["metadata"] = treeify_camera_metadata(cameras.metadata)

    return asdf.AsdfFile(tree)


# ------------------------------------------------------------------------------
# ---- Attributes --------------------------------------------------------------
# ------------------------------------------------------------------------------


def treeify_camera_attributes(attributes: CameraGroup.Attributes) -> dict:
    """Converts a collection of camera attributes to a tree."""

    df: pl.DataFrame = pl.DataFrame(
        [
            {
                "camera_key": identifier.key,
                "camera_label": identifier.label,
                "image_label": attributes.image_labels.get(identifier),
                "master_key": attributes.masters.get(identifier).key,
                "master_label": attributes.masters.get(identifier).label,
                "sensor_key": attributes.camera_sensors.get(identifier).key,
                "sensor_label": attributes.camera_sensors.get(identifier).label,
            }
            for identifier in attributes.identifiers
        ]
    )

    return df.to_dict(as_series=False)


# ------------------------------------------------------------------------------
# ---- References --------------------------------------------------------------
# ------------------------------------------------------------------------------


def treeify_camera_references(references: CameraGroup.References) -> dict:
    """Converts a collection of camera references to a tree."""

    items: list[dict] = list()
    for identifier in references.identifiers:

        location: list | None = references.locations.get(identifier)
        rotation: list | None = references.rotations.get(identifier)

        item: dict = {
            "camera_key": identifier.key,
            "camera_label": identifier.label,
        }

        if location:
            item.update(
                {
                    "longitude": location[0],
                    "latitude": location[1],
                    "height": location[2],
                }
            )

        if rotation:
            item.update(
                {
                    "yaw": rotation[0],
                    "pitch": rotation[1],
                    "roll": rotation[2],
                }
            )

        items.append(item)

    return pl.DataFrame(items).to_dict(as_series=False)


# ------------------------------------------------------------------------------
# ---- Sensor ------------------------------------------------------------------
# ------------------------------------------------------------------------------


def treeify_camera_sensor(sensor: Sensor) -> dict:
    """Converts camera sensors to a tree."""

    data: dict = {
        "identifier": {
            "key": sensor.identifier.key,
            "label": sensor.identifier.label,
        },
        "width": sensor.width,
        "height": sensor.height,
    }

    if sensor.calibration is not None:
        data.update(
            {"calibration": treeify_camera_calibration(sensor.calibration)}
        )

    if sensor.location is not None:
        data.update({"location": sensor.location})

    if sensor.rotation is not None:
        data.update({"rotation": sensor.rotation})

    return data


def treeify_camera_calibration(calibration: CameraCalibration) -> dict:
    """Converts a camera calibration to a tree."""
    data: dict = {
        "camera_matrix": calibration.camera_matrix,
        "distortion": calibration.distortion,
        "width": calibration.width,
        "height": calibration.height,
        "location": calibration.location,
        "rotation": calibration.rotation,
    }
    return data


# ------------------------------------------------------------------------------
# ---- Stereo ------------------------------------------------------------------
# ------------------------------------------------------------------------------


def treeify_stereo_rig(stereo: StereoRig) -> dict:
    """Converts a stereo camera and its rectification to a tree."""

    rectification: StereoRectificationResult = compute_stereo_rectification(
        left=stereo.sensors.first.calibration,
        right=stereo.sensors.second.calibration,
    )

    data: dict = {
        "sensors": {
            "first": treeify_camera_sensor(stereo.sensors.first),
            "second": treeify_camera_sensor(stereo.sensors.second),
        },
        "rectification": treeify_stereo_rectification(rectification),
    }

    return data


def treeify_stereo_rectification(
    rectification: StereoRectificationResult,
) -> dict:
    """Converts a stereo rectification to a tree."""
    data: dict = {
        "calibrations": {
            "first": treeify_camera_calibration(
                rectification.calibrations.first
            ),
            "second": treeify_camera_calibration(
                rectification.calibrations.second
            ),
        },
        "rectified_calibrations": {
            "first": treeify_camera_calibration(
                rectification.rectified_calibrations.first
            ),
            "second": treeify_camera_calibration(
                rectification.rectified_calibrations.second
            ),
        },
        "forward_pixel_maps": {
            "first": rectification.pixel_maps.first.to_array(),
            "second": rectification.pixel_maps.second.to_array(),
        },
        "inverse_pixel_maps": {
            "first": rectification.inverse_pixel_maps.first.to_array(),
            "second": rectification.inverse_pixel_maps.second.to_array(),
        },
        "transforms": {
            "rotation": rectification.transforms.rotation,
            "homographies": {
                "first": rectification.transforms.homographies.first,
                "second": rectification.transforms.homographies.second,
            },
        },
    }

    return data


# ------------------------------------------------------------------------------
# ---- Metadata ----------------------------------------------------------------
# ------------------------------------------------------------------------------


def treeify_camera_metadata(metadata: CameraGroup.Metadata) -> dict:
    """Converts a collection of camera metadata to a tree."""
    # TODO: Convert camera metadata to data frame

    items: list[dict] = list()
    for identifier, fields in metadata.fields.items():
        item: dict = {
            "camera_key": identifier.key,
            "camera_label": identifier.label,
        }
        item.update(fields)
        items.append(item)

    return pl.DataFrame(items).to_dict(as_series=False)
