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
- **Length**: Truncates generated values to `max_length`, leaving room for a collision suffix.
- **Type formatting**: Automatically formats dates, numbers, booleans
- **Unique and required**: Fields are always unique and cannot be empty
- **Read-only**: Fields are automatically set to read-only

## Field Properties

- `unique=True`: Always unique
- `editable=False`: Always read-only
- `blank=False`: Cannot be empty
- `null=False`: Cannot be NULL

## Development

CI checks the Python/Django test matrix, Ruff, Bandit (medium/high confidence
and severity), runtime dependency advisories, and package builds.

```bash
./service.py dev install-dev
./service.py dev test
```

## License

MIT

## CI packaging check

CI also installs the built wheel(s) in a clean environment and checks their
dependencies and imports without publishing. This installation check is
non-blocking during the initial rollout.

## Local audit

Install the project's development/test dependencies (including both local
packages where applicable), plus the audit tools:

```bash
python -m pip install ruff mypy bandit pip-audit vulture radon xenon pytest pytest-django pytest-cov build twine
make audit
```

Use the activated environment's Python, or pass `make audit PYTHON=/path/to/python`.
On systems without Make, run `python scripts/audit.py` directly. Git is required;
the geoaddress widget tests also require Node.js. The audit reports missing test
suites and runs all available checks even when earlier checks fail.
Xenon checks the absolute C, module B, and average A complexity thresholds. Existing
lint, typing, security, dependency, or test findings can make the audit fail.
CI also runs this audit as a non-blocking job and separately reports Radon maintainability without imposing a threshold.
