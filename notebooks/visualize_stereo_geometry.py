import marimo

__generated_with = "0.9.14"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Notebook for inspecting stereo results
        """
    )
    return


@app.cell
def __():
    from itertools import cycle
    from pathlib import Path
    from typing import Iterator, NamedTuple

    import cv2
    import numpy as np

    from mynd.image import ImageType, ImageComposite, ImageCompositeLoader
    from mynd.tasks.common import build_image_composite_loaders
    from mynd.visualization import (
        WindowHandle,
        KeyCode,
        create_image_visualizer,
        render_image,
        destroy_all_windows,
        colorize_values,
    )

    from mynd.utils.log import logger

    class InspectData(NamedTuple):

        label: str
        colors: np.ndarray
        ranges: np.ndarray

    def on_render(
        window: WindowHandle, colors: np.ndarray, ranges: np.ndarray
    ) -> None:
        """Callback to render during inspection."""
        stacked: np.ndarray = np.hstack((colors, ranges))
        render_image(window, stacked)

    def on_update(
        keys: Iterator[str], loaders: dict[str, ImageCompositeLoader]
    ) -> InspectData:
        """Callback to update during inspection."""
        key: str = next(keys)
        loader: ImageCompositeLoader = loaders.get(key)
        composite: ImageComposite = loader()

        colors: np.ndarray = composite.get(ImageType.COLOR).to_array()
        ranges: np.ndarray = composite.get(ImageType.RANGE).to_array()

        logger.info(
            f"Range statistics - min: {ranges.min():.2f}, max: {ranges.max():.2f}, mean: {ranges.mean():.2f}, median: {np.median(ranges):.2f}"
        )

        # Filter far points to improve visualization
        ranges: np.ndarray = colorize_values(
            ranges, lower=0.0, upper=8.0, flip=True
        )

        # Squeeze grayscale into 2D
        colors: np.ndarray = np.squeeze(colors)

        if colors.ndim == 2:
            colors: np.ndarray = np.stack([colors] * 3, axis=2)

        # TODO: Add statistics
        return InspectData(key, colors, ranges)

    def inspect_stereo_geometry(
        loaders: dict[str, ImageCompositeLoader]
    ) -> None:
        """Inspect stereo geometry by loading images and their correspond range map."""

        keys: Iterator[str] = cycle(sorted(list(loaders.keys())))
        data: InspectData = on_update(keys, loaders)

        assert data.colors is not None, "color map does not exist"
        assert data.ranges is not None, "range map does not exist"

        window: WindowHandle = create_image_visualizer(
            window_name="color", width=1360, height=512
        )

        while True:

            # On stereo inspect update
            on_render(window, data.colors, data.ranges)
            key: KeyCode = KeyCode(cv2.waitKey(0))

            match key:
                case KeyCode.SPACE:
                    data: InspectData = on_update(keys, loaders)
                case KeyCode.ESC:
                    destroy_all_windows()
                    logger.info("Quitting...")
                    return
                case _:
                    pass

    def main() -> None:
        """Main function."""

        # r29mrd5h_20090612_225306, r29mrd5h_20090613_100254, r29mrd5h_20110612_033752, r29mrd5h_20130611_002419
        # qdch0ftq_20100428_020202, qdch0ftq_20110415_020103, qdch0ftq_20120430_002423
        # r23m7ms0_20100606_001908, r23m7ms0_20120601_070118, r23m7ms0_20140616_044549
        # r23685bc_20100605_021022, r23685bc_20120530_233021, r23685bc_20140616_225022

        DEPLOYMENT: str = "r29mrd5h_20110612_033752"

        image_directories: dict[ImageType, Path] = {
            ImageType.COLOR: Path(
                f"/data/kingston_snv_01/acfr_images_grayworld/{DEPLOYMENT}_grayworld"
            ),
            ImageType.RANGE: Path(
                f"/data/kingston_snv_01/stereo_test/ranges/{DEPLOYMENT}_ranges"
            ),
            ImageType.NORMAL: Path(
                f"/data/kingston_snv_01/stereo_test/normals/{DEPLOYMENT}_normals"
            ),
        }

        for image_type, directory in image_directories.items():
            assert directory.exists(), f"directory does not exist: {directory}"

        loaders: dict[str, ImageCompositeLoader] = (
            build_image_composite_loaders(image_directories)
        )

        inspect_stereo_geometry(loaders)

    # INVOKE MAIN
    main()
    return (
        ImageComposite,
        ImageCompositeLoader,
        ImageType,
        InspectData,
        Iterator,
        KeyCode,
        NamedTuple,
        Path,
        WindowHandle,
        build_image_composite_loaders,
        colorize_values,
        create_image_visualizer,
        cv2,
        cycle,
        destroy_all_windows,
        inspect_stereo_geometry,
        logger,
        main,
        np,
        on_render,
        on_update,
        render_image,
    )


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
