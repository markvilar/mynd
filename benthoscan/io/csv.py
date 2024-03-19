from pathlib import Path
from typing import Dict, List

import pandas as pd

from loguru import logger
from result import Ok, Err, Result


def read_csv(path: Path) -> Result[Dict, str]:
    """Reads camera references from a CSV file."""
    try:
        data = pd.read_csv(path)
        return Ok(data.to_dict())
    except BaseException as error:
        return Err(str(error))
