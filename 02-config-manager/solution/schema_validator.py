from typing import Any


class SchemaValidator:
    """
    Validates config against a schema.
    """
    
    def __init__(self, schema: dict[str, type | tuple[type, ...]]) -> None:
        self._schema = schema
        
    def validate(self, config: dict[str, Any]) -> list[str]:
        """
        Validate the config against the schema.
        """
        errors: list[str] = []
        for key, expected_type in self._schema.items():
            value = self._get_nested(config, key)
            if value is None:
                errors.append(f"Missing required key: '{key}'")
                continue
            if not isinstance(value, expected_type):
                errors.append(
                    f"Type error for '{key}': expected {self._type_name(expected_type)}, "
                    f"got {type(value).__name__} (value: {value!r})"
                )

        return errors
    
    def _get_nested(self, config: dict[str, Any], key: str) -> Any:
        """
        Get a nested value from the config using dot notation.
        """
        keys = key.split(".")
        current = config
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return None
            current = current[k]
        return current
    
    def _type_name(self, t: type | tuple[type, ...]) -> str:
        """
        Get readable name for type(s).

        NEW CONCEPT — value!r in f-strings:
            !r calls repr() on the value — shows strings with quotes,
            which makes error messages clearer.
            f"{value!r}" → "'hello'" instead of "hello"
        """
        if isinstance(t, tuple):
            return " or ".join(cls.__name__ for cls in t)
        return t.__name__
    
    def __repr__(self) -> str:
        keys = list(self._schema.keys())
        return f"SchemaValidator(keys={keys})"
    
    
# ---------- QUICK TEST ----------
if __name__ == "__main__":
    schema = {
        "database.host": str,
        "database.port": int,
        "api.timeout": (int, float),  # allow both
        "debug": bool,
    }

    validator = SchemaValidator(schema)
    print(f"Validator: {validator}")

    # Valid config
    print("\n=== Valid Config ===")
    valid_config = {
        "database": {"host": "localhost", "port": 5432},
        "api": {"timeout": 30.5},
        "debug": True,
    }
    errors = validator.validate(valid_config)
    print(f"Errors: {errors}")  # Should be empty

    # Invalid config
    print("\n=== Invalid Config ===")
    invalid_config = {
        "database": {"host": "localhost", "port": "not_a_number"},  # wrong type
        "api": {},  # missing timeout
        # debug is missing entirely
    }
    errors = validator.validate(invalid_config)
    for e in errors:
        print(f"  ❌ {e}")