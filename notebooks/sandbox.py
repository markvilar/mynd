import marimo

__generated_with = "0.9.14"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        #### Test mynds packages in the sandbox
        """
    )
    return


@app.cell
def __(CameraGroup):
    from pathlib import Path

    import asdf
    import numpy as np
    import polars as pl
    import tqdm

    from mynd.backend import metashape
    from mynd.collections import GroupID
    from mynd.utils.log import logger
    from mynd.utils.result import Ok, Err, Result

    def main() -> None:
        """Main entrypoint."""

        PROJECT: Path = Path(
            "/data/kingston_snv_01/acfr_metashape_projects/qdch0ftq_aligned_with_metadata.psz"
        )
        _OUTPUT: Path = Path("/data/kingston_snv_01/camera_export")

        assert PROJECT.exists(), f"project does not exist: {PROJECT}"

        match metashape.load_project(PROJECT):
            case Ok(None):
                pass
            case Err(message):
                logger.error(message)

        identifier: GroupID = GroupID(key=0, label="qdch0ftq_20100428_020202")
        _cameras: CameraGroup = metashape.camera_services.retrieve_camera_group(
            identifier
        ).unwrap()

        # TODO: Write your code here

    # INVOKE MAIN
    main()
    return (
        Err,
        GroupID,
        Ok,
        Path,
        Result,
        asdf,
        logger,
        main,
        metashape,
        np,
        pl,
        tqdm,
    )


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
