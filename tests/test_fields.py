"""Tests for NamedIDField value formatting."""

from namedid.fields import NamedIDField


def test_format_value_folds_accents() -> None:
    field = NamedIDField(source_fields=["title"], max_length=100)
    assert field._format_value("Café") == "cafe"
    assert field._format_value("résumé") == "resume"
    assert field._format_value("naïve") == "naive"


def test_format_value_accents_with_spaces() -> None:
    field = NamedIDField(source_fields=["title"], max_length=100)
    assert field._format_value("Théâtre Saint-Étienne") == "theatre-saint-etienne"
