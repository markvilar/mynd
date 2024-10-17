"""Module for creating plotting figures."""

import plotly.graph_objects as go

from plotly.subplots import make_subplots


def create_subplots(
    rows: int,
    cols: int,
    row_heights: list[int] = None,
    column_widths: list[int] = None,
) -> go.Figure:
    """Creates a figure with subplots with placeholder titles."""

    if not row_heights:
        row_heights = [1] * rows
    if not column_widths:
        column_widths = [1] * cols

    subplot_titles: tuple[str] = tuple(
        f"Plot {index}" for index in range(rows * cols)
    )

    figure: go.Figure = make_subplots(
        rows=rows,
        cols=cols,
        row_heights=row_heights,
        column_widths=column_widths,
        subplot_titles=subplot_titles,
    )

    return figure
