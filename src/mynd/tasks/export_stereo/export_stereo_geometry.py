"""Module for exporting stereo geometry, including rectification results, range maps, and normal maps."""

from dataclasses import dataclass, field
from pathlib import Path


from mynd.utils.result import Result


@dataclass
class ExportStereoTask:
    """Facade class for stereo export task."""

    range_directory: Path
    normal_directory: Path

    # TODO: Add stereo estimation configuration
    stereo_config: object

    @dataclass
    class Result:
        """Class representing a task result."""

        write_errors: list[str] = field(default_factory=list)


def invoke_stereo_export_task(
    config: ExportStereoTask.config,
) -> Result[ExportStereoTask.Result, str]:
    """Invoke a stereo export task."""

    # TODO: Add config validation

    # Compute stereo range and normal maps and export
    # return perform_stereo_geometry(config)
    raise NotImplementedError
