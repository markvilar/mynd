""" Test module for benthoscans utility module. """

import tempfile
import unittest

from pathlib import Path
from typing import Dict

from result import Ok, Err, Result

from benthoscan.core.utils import read_config, write_config

class CommonTests(unittest.TestCase):
    """ Test case for the template library common functions. """

    def setUp(self) -> None:
        """ Method to initialize test case components. """

    def tearDown(self) -> None:
        """ Method to shut down test case components. """

    def test_config_write(self):
        """ Test string concatenation function. """
        config = dict()
        config["section"] = {
            "x" : 0.0,
            "y" : 1.0,
            "text" : "hello",
        }

        with tempfile.NamedTemporaryFile(suffix='.toml') as filehandle:
            filepath = Path(filehandle.name)

            write_result : Result[Path, str] = write_config(
                config = config, 
                path = filepath, 
                mode = "w",
            )
            
            match write_result:
                case Ok(path): print(f"wrote config to file: {path}")
                case Err(message): print(f"error when writing file: {message}")
            
            read_result : Result[Dict, str] = read_config(
                path = filepath, 
                mode = "r",
            )

            match read_result:
                case Ok(data): print(f"read config from file: {data}")
                case Err(message): print(f"error when reading file: {message}")

if __name__ == "__main__":
    unittest.main()
