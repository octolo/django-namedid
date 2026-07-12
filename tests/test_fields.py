"""Tests for NamedIDField value formatting."""

from datetime import date

import pytest

from namedid.fields import NamedIDField

from tests.app.models import Product


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


def _widget() -> Product:
    return Product(name="Widget", code=1, created_date=date(2024, 1, 1))


@pytest.mark.django_db
def test_pre_save_runs_uniqueness_query_by_default(django_assert_num_queries) -> None:
    field = Product._meta.get_field("named_id")
    with django_assert_num_queries(1):
        value = field.pre_save(_widget(), add=True)
    assert value == "widget-1-20240101"


@pytest.mark.django_db
def test_skip_uniqueness_check_avoids_query(django_assert_num_queries) -> None:
    field = Product._meta.get_field("named_id")
    product = _widget()
    product.namedid_skip_uniqueness_check = True
    with django_assert_num_queries(0):
        value = field.pre_save(product, add=True)
    assert value == "widget-1-20240101"


@pytest.mark.django_db
def test_skip_uniqueness_check_returns_base_value_despite_collision() -> None:
    """With the opt-in flag, no collision suffix is appended (caller guarantees uniqueness)."""
    field = Product._meta.get_field("named_id")
    Product.objects.create(name="Widget", code=1, created_date=date(2024, 1, 1))

    without_flag = field.pre_save(_widget(), add=True)
    assert without_flag == "widget-1-20240101-1"

    skipped = _widget()
    skipped.namedid_skip_uniqueness_check = True
    assert field.pre_save(skipped, add=True) == "widget-1-20240101"
