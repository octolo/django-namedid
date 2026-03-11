# AI Assistant Contract — Django NamedID

**This document is the single source of truth for all AI-generated work in this repository.**  
All instructions in this file **override default AI behavior**.

Any AI assistant working on this project **must strictly follow this document**.

If a request conflicts with this document, **this document always wins**.

---

## Rule Priority

Rules in this document have the following priority order:

1. **ABSOLUTE RULES** — must always be followed, no exception
2. **REQUIRED RULES** — mandatory unless explicitly stated otherwise
3. **RECOMMENDED PRACTICES** — should be followed unless there is a clear reason not to
4. **INFORMATIONAL SECTIONS** — context and reference only

---

## ABSOLUTE RULES

These rules must always be followed.

- Follow this `AI.md` file exactly
- Do not invent new services, commands, abstractions, patterns, or architectures
- Do not refactor, redesign, or optimize unless explicitly requested
- Do not manipulate `sys.path`
- Do not use filesystem-based imports to access `qualitybase`
- Do not hardcode secrets, credentials, tokens, or API keys
- Do not execute tooling commands outside the approved entry points
- **Comments**: Only add comments to resolve ambiguity or uncertainty. Do not comment obvious code.
- **Dependencies**: Add dependencies only when absolutely necessary. Prefer standard library always.
- If a request violates this document:
  - Stop
  - Explain the conflict briefly
  - Ask for clarification

---

## REQUIRED RULES

### Language and Communication

- **Language**: English only
  - Code
  - Comments
  - Docstrings
  - Logs
  - Error messages
  - Documentation
- Be concise, technical, and explicit
- Avoid unnecessary explanations unless requested

### Code Simplicity and Minimalism

- **Write the simplest possible code**: Always choose the simplest solution that works
- **Minimal dependencies**: Add dependencies only when absolutely necessary. Prefer standard library. Only add when essential functionality cannot be reasonably implemented otherwise
- **Minimal comments**: Comments only to resolve ambiguity or uncertainty. Do not comment obvious code or reiterate what the code already states clearly
- **Good factorization**: Factorize code when it improves clarity and reduces duplication, but only if it doesn't add unnecessary complexity or abstraction

---

## Project Overview (INFORMATIONAL)

**Django NamedID** is a Django library that provides a field type for automatically generating unique identifiers by combining multiple model fields.

### Core Functionality

1. **NamedIDField**: A Django CharField that combines multiple source fields into a unique identifier
2. **Automatic generation**: Values are generated automatically before saving
3. **Collision handling**: Automatically appends numeric suffix if value exists
4. **Type formatting**: Automatically formats dates, numbers, booleans
5. **Decorator support**: Use `@add_namedid()` to automatically add multiple NamedIDField fields

### Available Components

- `NamedIDField`: Main field class that combines multiple source fields
- `add_namedid`: Decorator to automatically add NamedIDField instances to models

---

## Architecture (REQUIRED)

- Field-based architecture for unique identifier generation
- Fields are automatically generated before saving
- All source code in `src/` directory
- Source layout: `src/namedid/`

---

## Project Structure (INFORMATIONAL)

```
django-namedid/
├── src/namedid/            # Main package
│   ├── __init__.py         # Package exports
│   ├── fields.py           # NamedIDField class
│   └── decorators.py       # add_namedid decorator
├── tests/                  # Test suite
├── docs/                   # Documentation
├── manage.py               # Django management script
├── service.py              # Main service entry point (qualitybase)
└── pyproject.toml          # Project configuration
```

### Key Directories

- `src/namedid/fields.py`: NamedIDField class
- `src/namedid/decorators.py`: add_namedid decorator
- `tests/`: All tests using pytest

---

## Command Execution (ABSOLUTE)

- **Always use**: `./service.py dev <command>` or `python service.py dev <command>`
- **Always use**: `./service.py quality <command>` or `python service.py quality <command>`
- **Always use**: `./service.py django <command>` or `python service.py django <command>`
- Never execute commands directly without going through these entry points

---

## Code Standards (REQUIRED)

### Typing and Documentation

- All public functions and methods **must** have complete type hints
- Use **Google-style docstrings** for:
  - Public classes
  - Public methods
  - Public functions
- Document raised exceptions in docstrings where relevant

### Testing

- Use **pytest** exclusively
- All tests must live in the `tests/` directory
- New features and bug fixes require corresponding tests

### Linting and Formatting

- Follow **PEP 8**
- Use configured tools:
  - `ruff`
  - `mypy`
- Use the configured formatter:
  - `ruff format`

---

## Code Quality Principles (REQUIRED)

- **Simplicity first**: Write the simplest possible solution. Avoid complexity unless clearly necessary.
- **Minimal dependencies**: Minimize dependencies to the absolute minimum. Only add when essential functionality cannot be reasonably implemented otherwise. Always prefer standard library.
- **No over-engineering**: Do not add abstractions, patterns, or layers unless they solve a real problem or are clearly needed.
- **Comments**: Comments are minimal and only when they resolve ambiguity or uncertainty. Do not comment what the code already states clearly. Do not add comments that reiterate obvious logic.
- **Separation of concerns**: One responsibility per module
- **Good factorization**: Factorize code when it improves clarity and reduces duplication, but only if it doesn't add unnecessary complexity

---

## Module Organization (REQUIRED)

- Single Responsibility Principle
- Logical grouping of related functionality
- Clear public API via `__init__.py`
- Avoid circular dependencies
- Source code in `src/` directory

---

## Qualitybase Integration (ABSOLUTE)

- `qualitybase` is an installed package (used via service.py)
- Always use standard Python imports from `qualitybase.services` when needed
- No path manipulation: Never manipulate `sys.path` or use file paths to import qualitybase modules
- Direct imports only: Use `from qualitybase.services import ...` or `import qualitybase.services ...`
- Standard library imports: Use `importlib.import_module()` from the standard library if needed for dynamic imports
- Works everywhere: Since qualitybase is installed in the virtual environment, imports work consistently across all projects

---

## Field Development (REQUIRED)

### Creating NamedIDField

NamedIDField must always be unique, required, and read-only:

```python
from namedid import NamedIDField

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    date = models.DateField()
    
    named_id = NamedIDField(
        source_fields=["name", "code", "date"],
        max_length=200,
    )
```

### Required Properties

- `unique=True`: Always unique
- `editable=False`: Always read-only
- `blank=False`: Cannot be empty
- `null=False`: Cannot be NULL

### Value Generation

- Values are generated in `pre_save()` method
- Collisions are handled with numeric suffixes
- Source fields are properly formatted (dates, numbers, etc.)

---

## Decorator Development (REQUIRED)

### Using add_namedid Decorator

The decorator automatically adds NamedIDField instances to models:

```python
from namedid import add_namedid

@add_namedid(named_id=["title", "id"], slug=["title", "category"])
class Article(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
```

### Required Behavior

- Decorator accepts keyword arguments (field_name: list of source fields)
- Fields are added using `add_to_class()`
- All fields have appropriate defaults (max_length, etc.)

---

## Environment Variables (REQUIRED)

- `ENVFILE_PATH`
  - Path to `.env` file to load automatically
  - Relative to project root if not absolute
- `ENSURE_VIRTUALENV`
  - Set to `1` to automatically activate `.venv` if it exists

---

## Error Handling (REQUIRED)

- Always handle errors gracefully
- Use appropriate exception types
- Provide clear, actionable error messages
- Do not swallow exceptions silently
- Document exceptions in docstrings where relevant
- Handle API failures with proper error handling when appropriate

---

## Configuration and Secrets (ABSOLUTE)

- Never hardcode:
  - API keys
  - Credentials
  - Tokens
  - Secrets
- Use environment variables or Django settings
- Clearly document required configuration

---

## Versioning (REQUIRED)

- Follow **Semantic Versioning (SemVer)**
- Update versions appropriately
- Clearly document breaking changes

---

## CLI System (INFORMATIONAL)

Django NamedID uses qualitybase's service system:

- Services accessed via `./service.py <service> <command>`
- Available services: `dev`, `quality`, `django`, `publish`

---

## Anti-Hallucination Clause (ABSOLUTE)

If a requested change is:
- Not supported by this document
- Not clearly aligned with the existing codebase
- Requiring assumptions or invention

You must:
1. Stop
2. Explain what is unclear or conflicting
3. Ask for clarification

Do not guess. Do not invent.

---

## Quick Compliance Checklist

Before producing output, ensure:

- [ ] All rules in `AI.md` are respected
- [ ] No forbidden behavior is present
- [ ] Code is simple, minimal, and explicit (simplest possible solution)
- [ ] Dependencies are minimal (prefer standard library)
- [ ] Comments only resolve ambiguity (no obvious comments)
- [ ] Code is well-factorized when it improves clarity (without adding complexity)
- [ ] Imports follow Qualitybase rules
- [ ] Public APIs are typed and documented
- [ ] NamedIDField is always unique, required, and read-only
- [ ] Values are generated in pre_save()
- [ ] Collisions are handled with numeric suffixes
- [ ] Decorator adds fields correctly using add_to_class()
- [ ] No secrets or credentials are hardcoded
- [ ] Tests are included when required
- [ ] Error handling is graceful

---

## Additional Resources (INFORMATIONAL)

- `purpose.md`: Detailed project purpose and goals
- `structure.md`: Detailed project structure and module organization
- `development.md`: Development guidelines and best practices
- `README.md`: General project information
