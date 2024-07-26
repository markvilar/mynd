"""Module for plotting functions various data types."""

import plotly.graph_objects as go

from benthoscan.registration import RegistrationResult
from benthoscan.spatial import decompose_transformation, decompose_rotation


def trace_registration_result(
    result: RegistrationResult,
    name: str,
    legendgroup: int,
    color: str = "blue",
) -> dict[str, go.Trace]:
    """Creates graph objects for a registration result. The fitness, error, and correspondence count
    are plotted in addition to the transformation components."""

    scale, rotation, translation = decompose_transformation(result.transformation)
    yaw, roll, pitch = decompose_rotation(rotation)

    traces: dict = dict()

    traces["fitness"] = go.Bar(
        name=name,
        x=["Fitness"],
        y=[result.fitness],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=True,
    )

    traces["rmse"] = go.Bar(
        name=name,
        x=["RMSE"],
        y=[result.inlier_rmse],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["correspondences"] = go.Bar(
        name=name,
        x=["Correspondences"],
        y=[len(result.correspondence_set)],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["scale"] = go.Bar(
        name=name,
        x=["Scale"],
        y=[scale],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["rotation"] = go.Bar(
        name=name,
        x=["Rz", "Ry", "Rx"],
        y=[yaw, pitch, roll],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["translation"] = go.Bar(
        name=name,
        x=["Tx", "Ty", "Tz"],
        y=[translation[0], translation[1], translation[2]],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    return traces
