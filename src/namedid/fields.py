from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


_NON_WORD_RE = re.compile(r'[^\w\-]')


class NamedIDField(models.CharField):
    """Field that combines multiple fields into a unique identifier with collision handling."""

    def __init__(
        self,
        source_fields: list[str],
        separator: str = "-",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.source_fields = source_fields
        self.separator = separator
        self._sep_collapse_re = re.compile(rf'{re.escape(separator)}+')
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
        value = self._compute_value(model_instance, add)
        setattr(model_instance, self.attname, value)
        return value

    def _compute_value(self, model_instance: Any, add: bool) -> str:
        base_value = self._generate_base_value(model_instance)
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

        return self._find_free_value(model_instance, base_value, add)

    def _find_free_value(self, model_instance: Any, base_value: str, add: bool) -> str:
        """Return ``base_value`` or ``base_value<sep>N`` such that no row collides.

        Performs a single query that fetches ``base_value`` and any
        ``base_value<sep>...`` row, then picks the lowest free counter
        in memory.
        """
        field_name = self.attname
        model_class = model_instance.__class__
        prefix = f"{base_value}{self.separator}"

        query = model_class.objects.filter(
            Q(**{field_name: base_value})
            | Q(**{f"{field_name}__startswith": prefix})
        )
        query = self._scope_filter(model_instance, query)
        if not add and model_instance.pk:
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

    def _resolve_field(self, instance: Any, path: str) -> Any:
        """Resolve a dot-separated attribute path starting from *instance*."""
        obj = instance
        for part in path.split('.'):
            if obj is None:
                return None
            obj = getattr(obj, part, None)
        return obj

    def _generate_base_value(self, model_instance: Any) -> str:
        values = []
        for field_name in self.source_fields:
            value = self._resolve_field(model_instance, field_name)
            if value is not None:
                values.append(self._format_value(value))
        return self.separator.join(values)

    def _format_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (date, datetime)):
            return value.strftime("%Y%m%d")
        if isinstance(value, (int, float)):
            return str(value)
        string_value = unicodedata.normalize("NFD", str(value))
        string_value = "".join(
            c for c in string_value if unicodedata.category(c) != "Mn"
        )
        string_value = string_value.lower().replace(" ", self.separator)
        string_value = _NON_WORD_RE.sub('', string_value)
        string_value = self._sep_collapse_re.sub(self.separator, string_value)
        return string_value.strip(self.separator)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['source_fields'] = self.source_fields
        if self.separator != "-":  # Only include if non-default
            kwargs['separator'] = self.separator
        kwargs.pop('editable', None)
        kwargs['blank'] = self.blank
        kwargs['null'] = self.null
        kwargs['unique'] = self._unique_scope if self._unique_scope is not None else self.unique
        return name, path, args, kwargs
