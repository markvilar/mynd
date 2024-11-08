import marimo

__generated_with = "0.9.14"
app = marimo.App()


@app.cell
def __():
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Optional

    import polars as pl

    from mynd.backend import metashape
    from mynd.camera import Camera
    from mynd.collections import CameraGroup
    from mynd.io import write_data_frame

    from mynd.utils.log import logger
    from mynd.utils.result import Ok, Err, Result


    CameraGroupID = CameraGroup.Identifier


    def tabulate_camera_identifiers(
        identifiers: list[Camera.Identifier],
    ) -> pl.DataFrame:
        """Converts a collection of camera identifiers to a data frame."""
        return pl.DataFrame(
            [
                {"camera_key": identifier.key, "camera_label": identifier.label}
                for identifier in identifiers
            ]
        )


    def tabulate_camera_references(
        references: CameraGroup.References,
    ) -> pl.DataFrame:
        """Converts a collection of camera references to a data frame."""
        entries: list[dict] = list()
        for index, identifier in enumerate(references.identifiers):

            location: list | None = references.locations.get(identifier)
            rotation: list | None = references.rotations.get(identifier)

            entry: dict = {
                "camera_key": identifier.key,
                "camera_label": identifier.label,
            }

            if location:
                entry.update(
                    {
                        "longitude": location[0],
                        "latitude": location[1],
                        "height": location[2],
                    }
                )

            if rotation:
                entry.update(
                    {"yaw": rotation[0], "pitch": rotation[1], "roll": rotation[2]}
                )

            entries.append(entry)

        return pl.DataFrame(entries)


    def tabulate_camera_metadata(metadata: CameraGroup.Metadata) -> pl.DataFrame:
        """Converts a collection of camera metadata to a data frame."""
        entries: list[dict] = list()
        for identifier, fields in metadata.fields.items():
            entry: dict = {
                "camera_key": identifier.key,
                "camera_label": identifier.label,
            }
            entry.update(fields)
            entries.append(entry)

        return pl.DataFrame(entries)


    @dataclass
    class Config:

        target: str
        destination: Path
        extension: str


    def process_camera_data(cameras: CameraGroup, config: Config) -> pl.DataFrame:
        """Process camera data from various sources."""

        data_frames: dict[str, pl.DataFrame] = {
            "identifiers": tabulate_camera_identifiers(
                cameras.attributes.identifiers
            ),
            "ref_estimates": tabulate_camera_references(
                cameras.reference_estimates
            ),
            "ref_priors": tabulate_camera_references(cameras.reference_priors),
            "metadata": tabulate_camera_metadata(cameras.metadata),
        }

        # Join identifiers, reference estimates, and metadata
        left: pl.DataFrame = data_frames.get("ref_estimates")
        for right in [data_frames.get("metadata")]:
            left: pl.DataFrame = left.join(
                right, how="left", on=["camera_key", "camera_label"]
            )

        cameras: pl.DataFrame = left

        # TODO: Add some fancy interpolation with reference priors
        cameras: pl.DataFrame = cameras.sort(by="timestamp")
        cameras: pl.DataFrame = cameras.with_columns(
            (-pl.col("height")).alias("negative_height")
        )

        # TODO: Filter out monochrome images
        cameras: pl.DataFrame = cameras.filter(
            pl.col("camera_label").str.ends_with("LC16")
        )
        cameras: pl.DataFrame = cameras.sort(by="camera_label")

        # Add file path
        cameras: pl.DataFrame = cameras.with_columns(
            pl.concat_str([pl.col("camera_label"), pl.lit(config.extension)]).alias(
                "image_path"
            )
        )

        return cameras


    def export_cameras_data_frame(config: Config) -> None:
        """Export cameras to a data frame."""

        target_group: CameraGroupID = retrieve_target_group(config.target)
        camera_group: CameraGroup = metashape.camera_services.retrieve_camera_group(
            target_group
        ).unwrap()

        # TODO: Add config to select base / sorting / interpolation

        # TODO: Create data frame for camera - attributes - identifiers
        processed_cameras: pl.DataFrame = process_camera_data(camera_group, config)

        logger.info("")
        logger.info(f"Shape:   {processed_cameras.shape}")
        logger.info(f"Columns: {processed_cameras.columns}")
        logger.info("")

        write_result: Result = write_data_frame(
            config.destination, processed_cameras
        )
        match write_result:
            case Ok(path):
                logger.info(f"Wrote processed cameras: {path}")
            case Err(message):
                logger.error(message)


    def retrieve_target_group(target: str) -> Optional[CameraGroupID]:
        """Retrieves the target group from the backend."""
        identifiers: list[CameraGroupID] = (
            metashape.get_group_identifiers().unwrap()
        )
        mapping: dict[str, CameraGroupID] = {
            identifier.label: identifier for identifier in identifiers
        }
        return mapping.get(target)


    def main() -> None:
        """Main function."""

        # r23m7ms0_20100606_001908
        # r23685bc_20100605_021022, r23685bc_20120530_233021, r23685bc_20140616_225022

        GROUP_LABEL: str = "r23m7ms0_20100606_001908"
        PROJECT: Path = Path(
            "/data/kingston_snv_01/acfr_metashape_projects_dev/r23m7ms0_lite_with_metadata.psz"
        )
        OUTPUT_DIR: Path = Path("/data/kingston_snv_01/georef_semantics_test")

        configs: list[Config] = [
            Config(
                f"{GROUP_LABEL}",
                Path(f"{OUTPUT_DIR}/{GROUP_LABEL}_cameras_grayworld.csv"),
                extension=".png",
            ),
            Config(
                f"{GROUP_LABEL}",
                Path(f"{OUTPUT_DIR}/{GROUP_LABEL}_cameras_debayered.csv"),
                extension=".tiff",
            ),
        ]

        load_result: Result = metashape.load_project(PROJECT)
        if load_result.is_err():
            logger.error(load_result.err())

        for config in configs:
            export_cameras_data_frame(config)


    # Invoke main function
    main()
    return (
        Camera,
        CameraGroup,
        CameraGroupID,
        Config,
        Err,
        Ok,
        Optional,
        Path,
        Result,
        dataclass,
        export_cameras_data_frame,
        logger,
        main,
        metashape,
        pl,
        process_camera_data,
        retrieve_target_group,
        tabulate_camera_identifiers,
        tabulate_camera_metadata,
        tabulate_camera_references,
        write_data_frame,
    )


if __name__ == "__main__":
    app.run()
