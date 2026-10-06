# django-namedid

Django field that automatically combines multiple fields into a unique identifier with collision handling.

## Purpose

Create unique identifiers by combining multiple model fields (e.g., name, id, date) with automatic collision resolution.

## Installation

```bash
pip install django-namedid
```

## Quick Start

### Using NamedIDField directly

```python
from django.db import models
from namedid import NamedIDField

class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    created_date = models.DateField()
    
    named_id = NamedIDField(
        source_fields=["name", "code", "created_date"],
        max_length=200,
    )
```

### Custom generator

The base value is built by `generate_namedid(instance, source_fields, separator)`. Pass `generator` to replace that function. It must use the same signature and return a string. Collision suffixes are still applied by the field.

```python
# myapp/generators.py
from namedid import generate_namedid

def custom_namedid(instance, source_fields, separator):
    base = generate_namedid(instance, source_fields, separator)
    return f"org{separator}{base}" if base else base
```

```python
named_id = NamedIDField(
    source_fields=["name"],
    generator="myapp.generators.custom_namedid",
    max_length=200,
)
```

`generator` also accepts the callable itself. A dotted path is the form migrations can store unchanged.

### Using the decorator

```python
from django.db import models
from namedid import add_namedid

@add_namedid(named_id=["title", "id"], slug=["title", "category"])
class Article(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    content = models.TextField()
```

## Features

- **Automatic generation**: Values are generated automatically before saving
- **Collision handling**: Automatically appends numeric suffix if value exists (e.g., `name-1-2023`, `name-1-2023-1`, `name-1-2023-2`)
- **Type formatting**: Automatically formats dates, numbers, booleans
- **Unique and required**: Fields are always unique and cannot be empty
- **Read-only**: Fields are automatically set to read-only

## Field Properties

- `unique=True`: Always unique
- `editable=False`: Always read-only
- `blank=False`: Cannot be empty
- `null=False`: Cannot be NULL

## Development

```bash
./service.py dev install-dev
./service.py dev test
```

## License

MIT
