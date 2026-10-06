from __future__ import annotations

import importlib
from typing import Any, cast

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .generators import NamedIDGenerator, generate_namedid


class NamedIDField(models.CharField):
    """CharField that builds a unique identifier from other fields.

    The base value comes from :func:`namedid.generate_namedid`, unless
    ``generator`` names another callable. The field still appends a numeric
    suffix when that base value collides.
    """

    def __init__(
        self,
        source_fields: list[str],
        separator: str = "-",
        *args: Any,
        generator: str | NamedIDGenerator | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the field.

        Args:
            source_fields: Dotted attribute paths combined into the identifier.
            separator: String inserted between formatted source values.
            *args: Passed through to ``CharField``.
            generator: Dotted path or callable that replaces the default
                generator. Called as ``generator(instance, source_fields,
                separator)`` and must return the base identifier as a string.
                Collision suffixes are still applied by the field. A callable
                must be importable at module level so migrations can serialize
                it. Defaults to :func:`namedid.generate_namedid`.
            **kwargs: Passed through to ``CharField``.

        Raises:
            ImportError: If ``generator`` is a dotted path that cannot be imported.
            TypeError: If ``generator`` is not a string, a callable, or ``None``.
        """
        self.source_fields = source_fields
        self.separator = separator
        self.generator = generator
        self._generator = _resolve_generator(generator)
        kwargs["editable"] = False
        if "blank" not in kwargs:
            kwargs["blank"] = False
        if "null" not in kwargs:
            kwargs["null"] = False
        unique_arg = kwargs.pop("unique", True)
        self._unique_scope = unique_arg if isinstance(unique_arg, (tuple, list)) else None
        kwargs["unique"] = False if self._unique_scope else unique_arg
        super().__init__(*args, **kwargs)

    def _scope_filter(self, model_instance: Any, queryset):
        """Apply scope filter when unique is a tuple of field names."""
        if not self._unique_scope:
            return queryset
        for field_name in self._unique_scope:
            value = getattr(model_instance, field_name, None)
            if value is not None:
                queryset = queryset.filter(**{field_name: value})
        return queryset

    def pre_save(self, model_instance: Any, add: bool) -> str:
        value = self._compute_value(model_instance)
        setattr(model_instance, self.attname, value)
        return value

    def _compute_value(self, model_instance: Any) -> str:
        base_value = self._generator(model_instance, self.source_fields, self.separator)
        if not isinstance(base_value, str):
            raise TypeError(
                f"Generator {self.generator!r} must return str, got {type(base_value).__name__}"
            )
        if not base_value:
            # Source fields unresolvable (e.g. historical mirror model without
            # the original properties): preserve the already-computed value.
            existing = getattr(model_instance, self.attname, None)
            if existing:
                return existing
            raise ValueError(
                _("Cannot generate named_id: all source fields %(fields)s are None or empty")
                % {"fields": self.source_fields}
            )

        if self._unique_scope is None and not self.unique:
            return base_value

        # Opt-in escape hatch for trusted bulk imports / migrations that already
        # guarantee uniqueness within the scope: skip the collision-resolution
        # query (one SELECT per row otherwise). Setting the attribute on the
        # instance is enough; unknown to older releases, so it degrades safely.
        if getattr(model_instance, "namedid_skip_uniqueness_check", False):
            return base_value

        # AutoField pk is assigned after pre_save on insert, so a source pk is
        # missing from the stored value. The next save would append it and look
        # like a collision suffix. Keep the stored value when the other sources
        # are unchanged.
        if self._stored_value_omits_only_pk(model_instance):
            return getattr(model_instance, self.attname)

        return self._find_free_value(model_instance, base_value)

    def _stored_value_omits_only_pk(self, model_instance: Any) -> bool:
        """True when the stored named id already matches the sources except the pk."""
        if not getattr(model_instance, "pk", None):
            return False
        existing = getattr(model_instance, self.attname, None)
        if not existing:
            return False
        pk = model_instance._meta.pk
        pk_paths = {pk.name, pk.attname, "pk"}
        if not any(path in pk_paths for path in self.source_fields):
            return False
        sources = [path for path in self.source_fields if path not in pk_paths]
        without_pk = self._generator(model_instance, sources, self.separator)
        return self._is_stored_variant(existing, without_pk)

    def _is_stored_variant(self, value: str, base: str) -> bool:
        """True when ``value`` is ``base`` or ``base<sep><counter>``."""
        if value == base:
            return True
        prefix = f"{base}{self.separator}"
        if not value.startswith(prefix):
            return False
        suffix = value[len(prefix) :]
        return suffix.isdecimal()

    def _find_free_value(self, model_instance: Any, base_value: str) -> str:
        """Return ``base_value`` or ``base_value<sep>N`` such that no row collides.

        Performs a single query that fetches ``base_value`` and any
        ``base_value<sep>...`` row, then picks the lowest free counter
        in memory.
        """
        field_name = self.attname
        model_class = model_instance.__class__
        prefix = f"{base_value}{self.separator}"

        query = model_class.objects.filter(
            Q(**{field_name: base_value}) | Q(**{f"{field_name}__startswith": prefix})
        )
        query = self._scope_filter(model_instance, query)
        if model_instance.pk:
            query = query.exclude(pk=model_instance.pk)

        taken = set(query.values_list(field_name, flat=True))
        if base_value not in taken:
            return base_value

        counter = 1
        while True:
            candidate = f"{prefix}{counter}"
            if candidate not in taken:
                return candidate
            counter += 1

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["source_fields"] = self.source_fields
        if self.separator != "-":
            kwargs["separator"] = self.separator
        if self.generator is not None:
            kwargs["generator"] = self.generator
        kwargs.pop("editable", None)
        kwargs["blank"] = self.blank
        kwargs["null"] = self.null
        kwargs["unique"] = self._unique_scope if self._unique_scope is not None else self.unique
        return name, path, args, kwargs


def _resolve_generator(generator: str | NamedIDGenerator | None) -> NamedIDGenerator:
    """Return the callable that builds the base named id."""
    if generator is None:
        return generate_namedid
    if isinstance(generator, str):
        return _import_generator(generator)
    if callable(generator):
        return generator
    raise TypeError(
        f"generator must be a dotted path or a callable, got {type(generator).__name__}"
    )


def _import_generator(path: str) -> NamedIDGenerator:
    """Import a generator from a ``package.module.function`` path."""
    module_path, separator, attr = path.rpartition(".")
    if not separator:
        raise ImportError(
            "generator must be a dotted path to a callable, "
            f"like 'package.module.function', got {path!r}"
        )
    module = importlib.import_module(module_path)
    try:
        func = getattr(module, attr)
    except AttributeError as exc:
        raise ImportError(
            f"Cannot import generator {path!r}: module {module_path!r} has no attribute {attr!r}"
        ) from exc
    if not callable(func):
        raise TypeError(f"Generator {path!r} must be callable")
    return cast(NamedIDGenerator, func)
