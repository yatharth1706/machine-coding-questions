# 02 — Config Manager

## Problem Statement

Design and implement a hierarchical configuration manager with dot notation access, environment overrides, change notification (observer pattern), and schema validation.

## Requirements

| Operation | Description | 
|-----------|-------------|
| `get(key, default?)` | Dot notation access: `"database.host"` |
| `set(key, value)` | Update value, notify observers |
| `load(config)` | Load/merge config dict (supports environments) |
| `set_environment(env)` | Switch between default/staging/production |
| `on_change(key, callback)` | Observer pattern — notify on value change |
| `validate()` | Type-check config against a schema |

## Data Structure

**Nested dict** with dot notation traversal (split on `.`, walk dict).

**Deep merge** for environment overrides — preserves keys not overridden.

```
base:   {"database": {"host": "localhost", "port": 5432}}
prod:   {"database": {"host": "prod-db"}}
merged: {"database": {"host": "prod-db", "port": 5432}}
                       ↑ overridden       ↑ preserved
```

## Architecture

```
ConfigManager (public API — composes all three)
├── ConfigStore       → nested dict storage, dot notation get/set, deep merge
├── ChangeNotifier    → observer pattern, parent key notifications
└── SchemaValidator   → type validation against schema
```

## Files

```
solution/
  config_store.py       → Nested dict + dot notation + deep merge
  change_notifier.py    → Observer pattern with parent key support
  schema_validator.py   → Type validation
  config_manager.py     → Public API composing all three
tests/
  test_config_manager.py → 35 pytest cases
```

## Key Patterns

- **Observer Pattern** — `on_change(key, callback)` for reactive config updates
- **Composition over Inheritance** — ConfigManager owns components, doesn't inherit
- **Deep Merge** — recursive dict merge preserving unoverridden keys
- **Dot Notation Traversal** — `"a.b.c"` → `data["a"]["b"]["c"]`

## New Python Concepts

- `copy.deepcopy` — independent copy of nested structures
- `defaultdict(list)` — auto-creates missing keys
- `Callable` type hint — typing for function parameters
- `__getitem__` / `__setitem__` — bracket syntax support
- `isinstance()` with tuple of types — multi-type checking
- `!r` in f-strings — repr formatting

## Run

```bash
# Demo
cd solution && python config_manager.py

# Tests
cd .. && uv run --with pytest pytest 02-config-manager/tests/ -v
```