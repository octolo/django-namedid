"""Generators referenced by dotted path in tests."""

from __future__ import annotations

from typing import Any

from namedid import generate_namedid


def uppercase_name(instance: Any, source_fields: list[str], separator: str) -> str:
    """Return the instance name in uppercase."""
    del source_fields, separator
    return str(getattr(instance, "name", "")).upper()


def custom_namedid(instance: Any, source_fields: list[str], separator: str) -> str:
    """Prefix the default named id with ``custom-``."""
    base = generate_namedid(instance, source_fields, separator)
    return f"custom-{base}" if base else base


NOT_A_GENERATOR = "nope"
