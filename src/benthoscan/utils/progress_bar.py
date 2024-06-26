"""Module for progress bar utilities."""

import dataclasses
import tqdm


@dataclasses.dataclass
class PercentBar():

    progress_bar: tqdm.tqdm = tqdm.tqdm(total=100.0)

    def update(self, percent: float) -> None:
        """TODO"""
        self.progress_bar.update(percent - self.progress_bar.n)


percent_bar = PercentBar()
