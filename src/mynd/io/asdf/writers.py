from pathlib import Path

import asdf

from mynd.utils.result import Ok, Err, Result


def write_tree(
    path: Path, tree: asdf.AsdfFile | dict, **options
) -> Result[None, str]:
    """Writes a tree to a file."""
    if isinstance(tree, dict):
        tree: asdf.AsdfFile = asdf.AsdfFile(tree)

    try:
        tree.write_to(path, **options)
    except BaseException as error:
        return Err(error)

    return Ok(None)
