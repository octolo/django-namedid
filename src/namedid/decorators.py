from __future__ import annotations

from typing import Callable, TypeVar

from .fields import NamedIDField

T = TypeVar("T")


def add_namedid(**fields_config: list[str]) -> Callable[[type[T]], type[T]]:
    """Decorator to automatically add NamedIDField fields to a Django model."""

    def decorator(cls: type[T]) -> type[T]:
        for field_name, source_fields in fields_config.items():
            field = NamedIDField(
                source_fields=source_fields,
                max_length=255,
            )
            cls.add_to_class(field_name, field)  # type: ignore[attr-defined]
        return cls

    return decorator
