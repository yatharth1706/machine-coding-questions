"""
ConfigManager — the main public API.

This is the Composition pattern in action:
    ConfigManager doesn't inherit from ConfigStore or ChangeNotifier.
    Instead, it OWNS instances of them and delegates work.

    Why composition over inheritance?
    - ConfigManager IS NOT a ConfigStore — it USES one
    - You can swap implementations (e.g., file-backed store vs in-memory)
    - Each component can be tested independently
    - Follows the principle: "favor composition over inheritance"

NEW CONCEPT — **kwargs:
    Collects extra keyword arguments into a dict.
    def func(**kwargs):  → kwargs is a dict of all extra named args
    func(a=1, b=2)      → kwargs = {"a": 1, "b": 2}

NEW CONCEPT — __getitem__ and __setitem__:
    __getitem__ → config["database.host"]     (bracket access)
    __setitem__ → config["database.host"] = x  (bracket assignment)
    These make your class feel like a dict.
"""

from typing import Any, Optional

from change_notifier import ChangeHandler, ChangeNotifier
from config_store import ConfigStore
from schema_validator import SchemaValidator


class ConfigManager:
    """
    Full-featured configuration manager with:
    - Dot notation access (get/set and bracket syntax)
    - Environment-based overrides (base → dev/staging/prod)
    - Observer pattern for change notifications
    - Schema validation

    Usage:
        config = ConfigManager()

        # Load base + environment configs
        config.load({
            "default": {
                "database": {"host": "localhost", "port": 5432},
                "debug": True,
            },
            "production": {
                "database": {"host": "prod-db.aws.com"},
                "debug": False,
            }
        })
        config.set_environment("production")

        config.get("database.host")  → "prod-db.aws.com"
        config.get("database.port")  → 5432  (inherited from default)
        config.get("debug")          → False (overridden by production)
    """

    def __init__(self) -> None:
        self._store = ConfigStore()
        self._notifier = ChangeNotifier()
        self._validator: Optional[SchemaValidator] = None

        # Store raw environment configs for switching later
        self._environments: dict[str, dict[str, Any]] = {}
        self._current_env: Optional[str] = None

    # ─── Loading ───────────────────────────────────────────────

    def load(self, config: dict[str, Any]) -> None:
        """
        Load config. Supports two formats:

        Simple (no environments):
            config.load({"database": {"host": "localhost"}})

        With environments (has "default" key):
            config.load({
                "default": {"database": {"host": "localhost"}},
                "production": {"database": {"host": "prod-db"}},
            })
        """
        if "default" in config:
            # Environment-aware config
            self._environments = config
            self._store = ConfigStore()
            self._store.load(config["default"])
            self._current_env = "default"
        else:
            # Simple config
            self._store.load(config)

    def set_environment(self, env: str) -> None:
        """
        Switch to a specific environment.
        Reloads from default + overlays the environment config.

        This means switching environments is clean — no leftover state
        from a previous environment.
        """
        if env not in self._environments:
            available = list(self._environments.keys())
            raise ValueError(f"Unknown environment: '{env}'. Available: {available}")

        # Start fresh from default
        self._store = ConfigStore()
        self._store.load(self._environments.get("default", {}))

        # Overlay environment-specific config (if not "default")
        if env != "default":
            self._store.load(self._environments[env])

        self._current_env = env

    # ─── Get / Set ─────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value using dot notation."""
        return self._store.get(key, default=default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value and notify observers if it changed.

        This is where ConfigStore and ChangeNotifier work together:
        1. ConfigStore handles the actual storage
        2. ChangeNotifier broadcasts the change to listeners
        """
        old_value, new_value = self._store.set(key, value)
        self._notifier.notify(key, old_value, new_value)

    def delete(self, key: str) -> bool:
        """Delete a key and notify observers."""
        old_value = self._store.get(key)
        deleted = self._store.delete(key)
        if deleted:
            self._notifier.notify(key, old_value, None)
        return deleted

    # ─── Observer Pattern ──────────────────────────────────────

    def on_change(self, key: str, handler: ChangeHandler) -> None:
        """Register a callback for when a key changes."""
        self._notifier.on_change(key, handler)

    def off_change(self, key: str, handler: ChangeHandler) -> bool:
        """Unregister a callback."""
        return self._notifier.off_change(key, handler)

    # ─── Validation ────────────────────────────────────────────

    def set_schema(self, schema: dict[str, type | tuple[type, ...]]) -> None:
        """Set a validation schema."""
        self._validator = SchemaValidator(schema)

    def validate(self) -> list[str]:
        """Validate current config against the schema. Returns list of errors."""
        if self._validator is None:
            return ["No schema set. Call set_schema() first."]
        return self._validator.validate(self._store.to_dict())

    # ─── Convenience / Dunder Methods ──────────────────────────

    def __getitem__(self, key: str) -> Any:
        """
        NEW CONCEPT — __getitem__:
            Lets you use bracket syntax: config["database.host"]
            Raises KeyError if key doesn't exist (dict-like behavior).
        """
        value = self._store.get(key)
        if value is None:
            raise KeyError(f"Config key not found: '{key}'")
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """
        NEW CONCEPT — __setitem__:
            Lets you use bracket assignment: config["debug"] = True
            Also triggers change notifications (delegates to self.set).
        """
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: if "database.host" in config"""
        return self._store.has(key)

    @property
    def environment(self) -> Optional[str]:
        """Current active environment."""
        return self._current_env

    @property
    def environments(self) -> list[str]:
        """List of available environments."""
        return list(self._environments.keys())

    def __repr__(self) -> str:
        return (
            f"ConfigManager(env={self._current_env}, "
            f"watchers={self._notifier.handler_count}, "
            f"data={self._store})"
        )


# ---------- FULL DEMO ----------
if __name__ == "__main__":
    config = ConfigManager()

    # ── Load with environments ──
    print("=" * 60)
    print("Config Manager Demo")
    print("=" * 60)

    config.load({
        "default": {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_dev",
            },
            "api": {
                "timeout": 30,
                "retries": 3,
            },
            "debug": True,
            "log_level": "DEBUG",
        },
        "staging": {
            "database": {
                "host": "staging-db.aws.com",
                "name": "myapp_staging",
            },
            "debug": True,
            "log_level": "INFO",
        },
        "production": {
            "database": {
                "host": "prod-db.aws.com",
                "name": "myapp_prod",
            },
            "debug": False,
            "log_level": "WARNING",
        },
    })

    print(f"\nEnvironments: {config.environments}")
    print(f"Current: {config.environment}")

    # ── Default environment ──
    print(f"\n--- Default Environment ---")
    print(f"database.host = {config.get('database.host')}")
    print(f"database.port = {config.get('database.port')}")
    print(f"debug = {config.get('debug')}")

    # ── Switch to production ──
    config.set_environment("production")
    print(f"\n--- Production Environment ---")
    print(f"database.host = {config.get('database.host')}")       # overridden
    print(f"database.port = {config.get('database.port')}")       # inherited from default
    print(f"database.name = {config.get('database.name')}")       # overridden
    print(f"debug = {config.get('debug')}")                       # overridden
    print(f"api.timeout = {config.get('api.timeout')}")           # inherited

    # ── Observer pattern ──
    print(f"\n--- Observer Pattern ---")
    change_log: list[str] = []

    def log_change(key: str, old: Any, new: Any) -> None:
        msg = f"CONFIG CHANGED: {key} = {old} → {new}"
        change_log.append(msg)
        print(f"  🔔 {msg}")

    config.on_change("database", log_change)
    config.set("database.host", "new-prod-db.aws.com")
    config.set("database.port", 5433)
    config.set("database.port", 5433)  # same value — no notification!

    # ── Bracket syntax ──
    print(f"\n--- Bracket Syntax ---")
    print(f"config['debug'] = {config['debug']}")
    config["log_level"] = "ERROR"
    print(f"config['log_level'] = {config['log_level']}")

    # ── 'in' operator ──
    print(f"\n--- Contains Check ---")
    print(f"'database.host' in config: {'database.host' in config}")
    print(f"'missing.key' in config: {'missing.key' in config}")

    # ── Schema validation ──
    print(f"\n--- Schema Validation ---")
    config.set_schema({
        "database.host": str,
        "database.port": int,
        "debug": bool,
        "api.timeout": (int, float),
        "log_level": str,
    })
    errors = config.validate()
    print(f"Validation errors: {errors if errors else 'None — all good!'}")

    # Break something and validate again
    config.set("database.port", "oops_not_a_number")
    errors = config.validate()
    print(f"\nAfter breaking port:")
    for e in errors:
        print(f"  ❌ {e}")

    print(f"\nChange log: {change_log}")