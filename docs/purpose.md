## Project Purpose

**Django NamedID** is a Django library that provides a field type for automatically generating unique identifiers by combining multiple model fields.

### Core Functionality

The library enables you to:

1. **Create unique identifiers** by combining multiple fields:
   - Automatically generate values from source fields (e.g., `name`, `id`, `date`)
   - Format values appropriately (dates as `YYYYMMDD`, numbers as strings, etc.)
   - Handle collisions by appending numeric suffixes

2. **NamedIDField**:
   - Automatically generates values before saving
   - Always unique and required
   - Read-only (cannot be edited)
   - Handles collisions automatically

3. **Decorator support**:
   - Use `@add_namedid()` decorator to automatically add multiple NamedIDField fields
   - Define multiple fields at once with different source field combinations

### Architecture

The library provides:

- **`NamedIDField`**: A Django CharField that combines multiple source fields
- **`add_namedid`**: A decorator to automatically add NamedIDField instances to models
- **Collision handling**: Automatic suffix generation when values already exist

### Use Cases

- Generate unique slugs from multiple fields
- Create composite identifiers for models
- Automatically handle unique constraint conflicts
- Generate human-readable unique identifiers
