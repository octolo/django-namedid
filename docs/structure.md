## Project Structure

Django NamedID follows a standard Python package structure with source code in `src/`.

### General Structure

```
django-namedid/
├── src/
│   └── namedid/              # Main package directory
│       ├── __init__.py      # Package exports (NamedIDField, add_namedid)
│       ├── fields.py        # NamedIDField class
│       └── decorators.py    # add_namedid decorator
├── tests/                   # Test suite
│   ├── settings.py          # Django test settings
│   └── app/                 # Test application
│       ├── models.py        # Test models
│       └── ...
├── docs/                    # Documentation
│   └── ...
├── manage.py                # Django management script
├── service.py               # Main service entry point (qualitybase)
├── pyproject.toml           # Project configuration
└── README.md                # Project README
```

### Module Organization Principles

- **Single Responsibility**: Each module has a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together
- **Source Layout**: All source code in `src/` directory

### Field Organization

The `fields.py` module provides:

- **`NamedIDField`**: Main field class that combines multiple source fields into a unique identifier

### Decorator Organization

The `decorators.py` module provides:

- **`add_namedid`**: Decorator to automatically add NamedIDField instances to Django models

### Package Exports

The public API is defined in `src/namedid/__init__.py`:

- **Fields**: `NamedIDField`
- **Decorators**: `add_namedid`
