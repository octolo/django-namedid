from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


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
        base_value = self._generate_base_value(model_instance)
        if not base_value:
            raise ValueError(
                _("Cannot generate named_id: all source fields %(fields)s are None or empty")
                % {"fields": self.source_fields}
            )

        field_name = self.attname
        model_class = model_instance.__class__

        if self._unique_scope is not None:
            # Uniqueness scoped by fields: add -1, -2... within that scope
            query = model_class.objects.filter(**{field_name: base_value})
            query = self._scope_filter(model_instance, query)
            if not add and hasattr(model_instance, "pk") and model_instance.pk:
                query = query.exclude(pk=model_instance.pk)

            if not query.exists():
                return base_value

            counter = 1
            while True:
                candidate = f"{base_value}{self.separator}{counter}"
                query = model_class.objects.filter(**{field_name: candidate})
                query = self._scope_filter(model_instance, query)
                if not add and hasattr(model_instance, "pk") and model_instance.pk:
                    query = query.exclude(pk=model_instance.pk)
                if not query.exists():
                    return candidate
                counter += 1
        elif self.unique:
            # Global uniqueness
            query = model_class.objects.filter(**{field_name: base_value})
            if not add and hasattr(model_instance, "pk") and model_instance.pk:
                query = query.exclude(pk=model_instance.pk)

            if not query.exists():
                return base_value

            counter = 1
            while True:
                candidate = f"{base_value}{self.separator}{counter}"
                query = model_class.objects.filter(**{field_name: candidate})
                if not add and hasattr(model_instance, "pk") and model_instance.pk:
                    query = query.exclude(pk=model_instance.pk)
                if not query.exists():
                    return candidate
                counter += 1
        else:
            return base_value

    def _generate_base_value(self, model_instance: Any) -> str:
        values = []
        for field_name in self.source_fields:
            value = getattr(model_instance, field_name, None)
            if value is not None:
                formatted_value = self._format_value(value)
                values.append(str(formatted_value))
        return self.separator.join(values)

    def _format_value(self, value: Any) -> str:
        if isinstance(value, (date, datetime)):
            return value.strftime("%Y%m%d")
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, bool):
            return "1" if value else "0"
        string_value = str(value)
        string_value = string_value.lower()
        string_value = string_value.replace(" ", self.separator)
        string_value = re.sub(r'[^\w\-]', '', string_value)
        string_value = re.sub(rf'{re.escape(self.separator)}+', self.separator, string_value)
        string_value = string_value.strip(self.separator)
        return string_value

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