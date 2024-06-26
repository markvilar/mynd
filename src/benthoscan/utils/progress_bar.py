"""Module for progress bar utilities."""

import dataclasses
import tqdm

from typing import Optional


@dataclasses.dataclass
class PercentBar:

    progress_bar: Optional[tqdm.tqdm] = None

    def prepare(self) -> None:
        """TODO"""
        self.progress_bar = tqdm.tqdm(total=100.0)

    def update(self, percent: float) -> None:
        """TODO"""
        self.progress_bar.update(percent - self.progress_bar.n)


def percent_bar() -> PercentBar:
    """Returns a percent bar."""
    return PercentBar()
