"""Django NamedID - Field that combines multiple fields into a unique identifier."""

__version__ = "0.1.0"

from .decorators import add_namedid
from .fields import NamedIDField

__all__ = [
    "NamedIDField",
    "add_namedid",
]
