"""Default named-id generator and the callable contract custom generators follow."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from datetime import date, datetime
from typing import Any


_NON_WORD_RE = re.compile(r"[^\w\-]")

NamedIDGenerator = Callable[[Any, list[str], str], str]


def generate_namedid(
    instance: Any,
    source_fields: list[str],
    separator: str = "-",
) -> str:
    """Build a named id from source field values on ``instance``.

    Resolves each dotted path in ``source_fields``, formats the value, and
    joins the results with ``separator``. Missing values (``None``) are
    skipped. An empty string means every source value was missing.

    Custom generators passed to :class:`namedid.NamedIDField` must use this
    signature. They can call this function and adjust the result.

    Args:
        instance: Object to read values from, usually a model instance.
        source_fields: Dotted attribute paths resolved from ``instance``.
        separator: String inserted between formatted values.

    Returns:
        The joined base identifier, without a collision suffix.
    """
    values: list[str] = []
    for field_name in source_fields:
        value = _resolve_field(instance, field_name)
        if value is not None:
            values.append(_format_value(value, separator))
    return separator.join(values)


def _resolve_field(instance: Any, path: str) -> Any:
    """Resolve a dotted attribute path starting from ``instance``."""
    obj = instance
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def _format_value(value: Any, separator: str) -> str:
    """Format one source value the way the default named id expects."""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y%m%d")
    if isinstance(value, (int, float)):
        return str(value)
    string_value = unicodedata.normalize("NFD", str(value))
    string_value = "".join(c for c in string_value if unicodedata.category(c) != "Mn")
    string_value = string_value.lower().replace(" ", separator)
    string_value = _NON_WORD_RE.sub("", string_value)
    collapsed = re.sub(rf"{re.escape(separator)}+", separator, string_value)
    return collapsed.strip(separator)
