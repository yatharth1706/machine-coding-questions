import copy
from typing import Any


class ConfigStore:
    """
    Nested dict that stores the config.
    
    Usage:
        store = ConfigStore()
        store.load({"database": {"host": "localhost", "port": 5432}})
        store.get("database.host")
        store.get("database")
        store.set("database.host", "prod")
        store.get("missing", default="default")
    """
    
    def __init__(self):
        self._data: dict[str, Any] = {}
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the config store.
        """
        keys = key.split(".")
        current = self._data
        
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return default
            current = current[k]
            
        # return a deep copy of dicts to prevent modification of the original data
        if isinstance(current, dict):
            return copy.deepcopy(current)

        return current
    
    def set(self, key: str, value: Any) -> tuple[Any, Any]:
        """
        Set a value in the config store.
        """
        keys = key.split(".")
        current = self._data
        
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                current[k] = {}
            current = current[k]
        
        last_key = keys[-1]
        old_value = current.get(last_key)
        current[last_key] = value
        return old_value, value
        
    def delete(self, key: str) -> bool:
        """
        Delete a value from the config store.
        """
        keys = key.split(".")
        current = self._data
        
        for k in keys[:-1]:
            if not isinstance(current, dict):
                return False
            current = current[k]
            
        last_key = keys[-1]
        if isinstance(current, dict) and last_key in current:
            del current[last_key]
            return True
        return False
    
    def load(self, config: dict[str, Any]) -> None:
        """
        Load a config into the config store by merging with the existing data.
        """
        self._data = self._deep_merge(config, self._data)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        Merge two dictionaries recursively.
        """
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result
    
    def has(self, key: str) -> bool:
        """
        Check if a value exists in the config store.
        """
        return self.get(key) is not None
    
    def __repr__(self) -> str:
        """
        Return a string representation of the config store.
        """
        return f"ConfigStore(data={self._data})"
        
        
# ---------- QUICK TEST ----------

if __name__ == "__main__":
    store = ConfigStore()
    
    # Load base config
    store.load({
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "password"
            }
        },
        "api": {
            "timeout": 10,
            "retries": 3
        }
    })
    
    print("=== Dot Notation Get ===")
    print(f"database.host: {store.get('database.host')}")
    print(f"database.port: {store.get('database.port')}")
    print(f"database.credentials.username: {store.get('database.credentials.username')}")
    print(f"database.credentials.password: {store.get('database.credentials.password')}")
    print(f"api.timeout: {store.get('api.timeout')}")
    print(f"api.retries: {store.get('api.retries')}")
    
    print("\n=== Set ===")
    old, new = store.set("database.host", "prod-db.com")
    print(f"Changed database.host from {old} to {new}")
    print(f"database.port: {store.get('database.port')}")
    print(f"database.credentials.username: {store.get('database.credentials.username')}")
    
    # Set a deeply nested key that doesn't exist yet
    store.set("feature_flags.dark_mode.enabled", True)
    print(f"feature_flags.dark_mode.enabled: {store.get('feature_flags.dark_mode.enabled')}")
    
    print("\n=== Deep Merge ===")
    store.load({
        "database": {
            "host": "prod-db.com",
        },
        "cache": {
            "ttl": 300  # new section
        }
    })
    print(f"cache.ttl: {store.get('cache.ttl')}")
    print(f"database.host: {store.get('database.host')}")
    print(f"database.port: {store.get('database.port')}")
    
    print("\n=== Delete ===")
    deleted = store.delete("cache.ttl")
    print(f"Deleted cache.ttl: {deleted}")
    print(f"cache.ttl: {store.get('cache.ttl', default="GONE")}")