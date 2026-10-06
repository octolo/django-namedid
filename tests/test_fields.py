"""Tests for NamedIDField value formatting and custom generators."""

from datetime import date
from types import SimpleNamespace
from typing import Any

import pytest

from namedid import generate_namedid
from namedid.fields import NamedIDField

from tests.app.models import Article, Product
from tests.generators import uppercase_name


def test_generate_namedid_folds_accents() -> None:
    assert generate_namedid(SimpleNamespace(title="Café"), ["title"]) == "cafe"
    assert generate_namedid(SimpleNamespace(title="résumé"), ["title"]) == "resume"
    assert generate_namedid(SimpleNamespace(title="naïve"), ["title"]) == "naive"


def test_generate_namedid_accents_with_spaces() -> None:
    instance = SimpleNamespace(title="Théâtre Saint-Étienne")
    assert generate_namedid(instance, ["title"]) == "theatre-saint-etienne"


def test_generate_namedid_bool_returns_numeric() -> None:
    assert generate_namedid(SimpleNamespace(flag=True), ["flag"]) == "1"
    assert generate_namedid(SimpleNamespace(flag=False), ["flag"]) == "0"


def test_generate_namedid_int_and_float() -> None:
    assert generate_namedid(SimpleNamespace(n=42), ["n"]) == "42"
    assert generate_namedid(SimpleNamespace(n=3.14), ["n"]) == "3.14"


def test_generate_namedid_date() -> None:
    assert generate_namedid(SimpleNamespace(d=date(2024, 1, 9)), ["d"]) == "20240109"


def test_generate_namedid_collapses_separators_and_strips() -> None:
    assert generate_namedid(SimpleNamespace(title="  Hello   World  "), ["title"]) == "hello-world"
    assert generate_namedid(SimpleNamespace(title="---weird---"), ["title"]) == "weird"


def test_generate_namedid_custom_separator() -> None:
    assert (
        generate_namedid(SimpleNamespace(title="Hello World"), ["title"], separator="_")
        == "hello_world"
    )
    assert (
        generate_namedid(SimpleNamespace(title="Café au lait"), ["title"], separator="_")
        == "cafe_au_lait"
    )


def test_generate_namedid_resolves_dotted_paths_and_skips_missing() -> None:
    instance = SimpleNamespace(
        name="Widget",
        code=None,
        category=SimpleNamespace(label="Tools"),
    )
    assert generate_namedid(instance, ["name", "code", "category.label"]) == "widget-tools"


def test_default_field_deconstruct_omits_generator() -> None:
    field = Product._meta.get_field("named_id")
    _, _, _, kwargs = field.deconstruct()
    assert "generator" not in kwargs


def _named_field(**kwargs: Any) -> NamedIDField:
    field = NamedIDField(max_length=100, **kwargs)
    field.set_attributes_from_name("named_id")
    return field


def _widget() -> Product:
    return Product(name="Widget", code=1, created_date=date(2024, 1, 1))


@pytest.mark.django_db
def test_resave_does_not_append_pk_to_named_id() -> None:
    article = Article.objects.create(title="Hello", category="News", content="x")
    assert article.named_id == "hello"
    assert article.slug == "hello-news"

    article.save()
    article.refresh_from_db()
    assert article.named_id == "hello"
    assert article.slug == "hello-news"


@pytest.mark.django_db
def test_resave_keeps_collision_suffix() -> None:
    Article.objects.create(title="Hello", category="News", content="x")
    duplicate = Article.objects.create(title="Hello", category="Other", content="y")
    assert duplicate.named_id == "hello-1"

    duplicate.save()
    duplicate.refresh_from_db()
    assert duplicate.named_id == "hello-1"


@pytest.mark.django_db
def test_source_change_still_regenerates_named_id() -> None:
    article = Article.objects.create(title="Hello", category="News", content="x")
    article.title = "Goodbye"
    article.save()
    article.refresh_from_db()
    assert article.named_id == "goodbye-1"
    assert article.slug == "goodbye-news"


@pytest.mark.django_db
def test_resave_keeps_product_named_id() -> None:
    product = Product.objects.create(name="Widget", code=1, created_date=date(2024, 1, 1))
    product.save()
    product.refresh_from_db()
    assert product.named_id == "widget-1-20240101"
    assert product.named_id_custom == "custom-widget-1-20240101"


@pytest.mark.django_db
def test_product_named_id_custom_uses_custom_generator() -> None:
    product = Product.objects.create(name="Widget", code=1, created_date=date(2024, 1, 1))
    assert product.named_id == "widget-1-20240101"
    assert product.named_id_custom == "custom-widget-1-20240101"


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


def test_generator_callable_receives_instance_and_field_options() -> None:
    seen: dict[str, Any] = {}

    def spy(instance: Any, source_fields: list[str], separator: str) -> str:
        seen["instance"] = instance
        seen["source_fields"] = list(source_fields)
        seen["separator"] = separator
        return "ok"

    instance = SimpleNamespace(name="Widget")
    field = _named_field(
        source_fields=["name", "code"],
        separator="_",
        generator=spy,
        unique=False,
    )
    assert field.pre_save(instance, add=True) == "ok"
    assert seen == {
        "instance": instance,
        "source_fields": ["name", "code"],
        "separator": "_",
    }


def test_generator_callable_is_serialized_by_deconstruct() -> None:
    field = _named_field(source_fields=["name"], generator=uppercase_name)
    _, _, _, kwargs = field.deconstruct()
    assert kwargs["generator"] is uppercase_name


@pytest.mark.django_db
def test_generator_dotted_path_replaces_default_and_keeps_collision_suffix() -> None:
    field = _named_field(
        source_fields=["name"],
        generator="tests.generators.uppercase_name",
    )
    existing = Product.objects.create(name="Widget", code=1, created_date=date(2024, 1, 1))
    Product.objects.filter(pk=existing.pk).update(named_id="WIDGET")

    assert field.pre_save(_widget(), add=True) == "WIDGET-1"


def test_generator_dotted_path_is_serialized_as_given() -> None:
    field = _named_field(
        source_fields=["name"],
        generator="tests.generators.uppercase_name",
    )
    _, _, _, kwargs = field.deconstruct()
    assert kwargs["generator"] == "tests.generators.uppercase_name"


def test_empty_generator_result_raises_when_nothing_is_stored() -> None:
    def empty(instance: Any, source_fields: list[str], separator: str) -> str:
        del instance, source_fields, separator
        return ""

    field = _named_field(source_fields=["name"], generator=empty, unique=False)
    with pytest.raises(ValueError, match="Cannot generate named_id"):
        field.pre_save(SimpleNamespace(), add=True)


def test_generator_must_return_str() -> None:
    def returns_int(instance: Any, source_fields: list[str], separator: str) -> str:
        del instance, source_fields, separator
        return 1  # type: ignore[return-value]

    field = _named_field(source_fields=["name"], generator=returns_int, unique=False)
    with pytest.raises(TypeError, match="must return str"):
        field.pre_save(SimpleNamespace(), add=True)


def test_generator_path_must_be_importable() -> None:
    with pytest.raises(ImportError):
        NamedIDField(source_fields=["name"], generator="does.not.exist", max_length=10)
    with pytest.raises(ImportError, match="dotted path"):
        NamedIDField(source_fields=["name"], generator="generate_namedid", max_length=10)
    with pytest.raises(ImportError, match="no attribute"):
        NamedIDField(
            source_fields=["name"],
            generator="tests.generators.missing",
            max_length=10,
        )


def test_generator_path_must_point_at_a_callable() -> None:
    with pytest.raises(TypeError, match="must be callable"):
        NamedIDField(
            source_fields=["name"],
            generator="tests.generators.NOT_A_GENERATOR",
            max_length=10,
        )


def test_generator_rejects_unsupported_types() -> None:
    with pytest.raises(TypeError, match="dotted path or a callable"):
        NamedIDField(source_fields=["name"], generator=1, max_length=10)  # type: ignore[arg-type]
