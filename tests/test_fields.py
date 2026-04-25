"""Tests for NamedIDField value formatting."""

from datetime import date

from namedid.fields import NamedIDField


def test_format_value_folds_accents() -> None:
    field = NamedIDField(source_fields=["title"], max_length=100)
    assert field._format_value("Café") == "cafe"
    assert field._format_value("résumé") == "resume"
    assert field._format_value("naïve") == "naive"


def test_format_value_accents_with_spaces() -> None:
    field = NamedIDField(source_fields=["title"], max_length=100)
    assert field._format_value("Théâtre Saint-Étienne") == "theatre-saint-etienne"


def test_format_value_bool_returns_numeric() -> None:
    field = NamedIDField(source_fields=["flag"], max_length=10)
    assert field._format_value(True) == "1"
    assert field._format_value(False) == "0"


def test_format_value_int_and_float() -> None:
    field = NamedIDField(source_fields=["n"], max_length=10)
    assert field._format_value(42) == "42"
    assert field._format_value(3.14) == "3.14"


def test_format_value_date() -> None:
    field = NamedIDField(source_fields=["d"], max_length=10)
    assert field._format_value(date(2024, 1, 9)) == "20240109"


def test_format_value_collapses_separators_and_strips() -> None:
    field = NamedIDField(source_fields=["title"], max_length=100)
    assert field._format_value("  Hello   World  ") == "hello-world"
    assert field._format_value("---weird---") == "weird"


def test_format_value_custom_separator() -> None:
    field = NamedIDField(source_fields=["title"], separator="_", max_length=100)
    assert field._format_value("Hello World") == "hello_world"
    assert field._format_value("Café au lait") == "cafe_au_lait"
