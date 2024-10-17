"""Module for literal functionality."""

import ast

from typing import Optional


Primitive = int | str | float | bool | None


def literal_primitive(literal: str) -> Optional[Primitive]:
    """Evaluate a string as a dtype."""
    try:
        evaluated: Primitive = ast.literal_eval(literal)
        return evaluated
    except ValueError:
        return None
