"""Django NamedID - Field that combines multiple fields into a unique identifier."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-namedid")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .decorators import add_namedid
from .fields import NamedIDField

__all__ = [
    "NamedIDField",
    "add_namedid",
]
