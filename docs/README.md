## Assistant Guidelines

This file provides general guidelines for the AI assistant working on this project.

For detailed information, refer to:
- `AI.md` - Condensed reference guide for AI assistants (start here)
- `purpose.md` - Project purpose and goals
- `structure.md` - Project structure and module organization
- `development.md` - Development guidelines and best practices

### Quick Reference

- Always use `./service.py dev <command>` or `python service.py dev <command>` for project tooling
- Always use `./service.py quality <command>` or `python service.py quality <command>` for quality checks
- Always use `./service.py django <command>` or `python service.py django <command>` for Django commands
- Maintain clean module organization and separation of concerns
- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation snippets, etc.)
- Follow Python best practices and quality standards
- Keep dependencies minimal and prefer standard library
- Ensure all public APIs have type hints and docstrings
- Write tests for new functionality
- Source code in `src/` directory

### Django NamedID-Specific Guidelines

- **Field development**: NamedIDField must always be unique, required, and read-only
- **Decorator development**: The add_namedid decorator should add fields dynamically to models
- **Collision handling**: Always handle collisions by appending numeric suffixes
- **Value generation**: Values must be generated automatically before saving

### Field Implementation Checklist

When working with NamedIDField:
- [ ] Field is always unique (`unique=True`)
- [ ] Field is always required (`blank=False`, `null=False`)
- [ ] Field is always read-only (`editable=False`)
- [ ] Values are generated in `pre_save()`
- [ ] Collisions are handled with numeric suffixes
- [ ] Source fields are properly formatted (dates, numbers, etc.)

### Decorator Implementation Checklist

When working with add_namedid decorator:
- [ ] Decorator accepts keyword arguments (field_name: list of source fields)
- [ ] Fields are added using `add_to_class()`
- [ ] All fields have appropriate defaults (max_length, etc.)
