from collections import defaultdict
from typing import Any, Callable


# A change handler receives: (key, old_value, new_value)
ChangeHandler = Callable[[str, Any, Any], None]

class ChangeNotifier:
    """
    Notifies observers when a value in the config store changes.
    """
    
    def __init__(self):
        self._handlers: dict[str, list[ChangeHandler]] = defaultdict(list)
    
    def on_change(self, key: str, handler: ChangeHandler) -> None:
        """
        Register a change handler for a given key.
        """
        if handler not in self._handlers[key]:
            self._handlers[key].append(handler)
            
    def off_change(self, key: str, handler: ChangeHandler) -> bool:
        """
        Unregister a change handler for a given key.
        """
        if handler in self._handlers[key]:
            self._handlers[key].remove(handler)
            # cleanup empty lists
            if not self._handlers[key]:
                del self._handlers[key]
            return True
        return False
    
    def notify(self, key: str, old_value: Any, new_value: Any) -> int:
        """
        Notify all change handlers for a given key.
        """
        if old_value == new_value:
            return 0
        
        called = 0
        
        # fire exact match handlers
        for handler in self._handlers[key]:
            handler(key, old_value, new_value)
            called += 1
            
        # fire parent key handlers
        parts = key.split(".")
        for i in range(1, len(parts)):
            parent_key = ".".join(parts[:i])
            for handler in self._handlers[parent_key]:
                handler(parent_key, old_value, new_value)
                called += 1
                
        return called
    
    @property
    def handler_count(self) -> int:
        """
        Return the total number of change handlers registered.
        """
        return sum(len(handlers) for handlers in self._handlers.values())
    
    def __repr__(self) -> str:
        """
        Return a string representation of the change notifier.
        """
        keys = list(self._handlers.keys())
        return f"ChangeNotifier(watching={keys}, total_handlers={self.handler_count})"
    

# ---------- QUICK TEST ----------

if __name__ == "__main__":
    notifier = ChangeNotifier()
    events_log: list[str] = []

    # Register handlers
    def on_db_change(key: str, old: Any, new: Any) -> None:
        msg = f"[DB] {key}: {old} → {new}"
        events_log.append(msg)
        print(msg)

    def on_host_change(key: str, old: Any, new: Any) -> None:
        msg = f"[HOST] {key}: {old} → {new}"
        events_log.append(msg)
        print(msg)

    notifier.on_change("database", on_db_change)         # parent listener
    notifier.on_change("database.host", on_host_change)  # exact listener

    print(f"Notifier: {notifier}")

    print("\n=== Notify: database.host changed ===")
    count = notifier.notify("database.host", "localhost", "prod-db")
    print(f"Handlers called: {count}")  # Should be 2 (host + parent db)

    print("\n=== Notify: same value (no change) ===")
    count = notifier.notify("database.host", "prod-db", "prod-db")
    print(f"Handlers called: {count}")  # Should be 0

    print("\n=== Unregister host handler ===")
    removed = notifier.off_change("database.host", on_host_change)
    print(f"Removed: {removed}")

    print("\n=== Notify again after unregister ===")
    count = notifier.notify("database.host", "prod-db", "staging-db")
    print(f"Handlers called: {count}")  # Should be 1 (only parent db)

    print(f"\nAll events: {events_log}")