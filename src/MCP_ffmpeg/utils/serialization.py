"""
This file contains the utils methods to serialize given data in structured format
"""

from typing import Any
from enum import Enum
from pathlib import Path
import json


def freeze(value: Any) -> Any:
    """
    This method converts the arbitrary Python objects into a JSON-serializable, deterministic structure.
    This makes hashing stable even for nested lists/dicts/Paths/enums/etc.

    :param value: Any value given
    :return: serialized value
    """

    if isinstance(value, Enum):
        return {"__enum__": f"{value.__class__.__name__}.{value.name}", "value": value.value}

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, Path):
        # normalize path to a consistent string representation
        return {"__path__": str(value)}

    if isinstance(value, (list, tuple, set)):
        # sets are unordered -> sort frozen values deterministically
        frozen_items = [freeze(v) for v in value]
        if isinstance(value, set):
            return {"__set__": sorted(frozen_items, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))}
        return frozen_items  # list/tuple keep order

    if isinstance(value, dict):
        # dict order shouldn't matter -> sort keys
        return {str(k): freeze(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}

    # fallback: stable-ish representation
    # If you pass custom objects, prefer passing primitive fields instead.
    return {"__repr__": repr(value)}