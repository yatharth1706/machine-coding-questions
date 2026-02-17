# Config Manager — Thought Process

## Phase 1: Clarify Requirements

**Functional:**
- Hierarchical/nested config storage (like JSON/YAML)
- Dot notation access: `config.get("database.host")` → walks nested dicts
- Environment overrides: base config + env-specific overrides (dev, prod, staging)
- Hot-reload: `on_change(key, callback)` — notify listeners when values change
- Type validation: validate config against a schema (key → expected type)
- Default values: `config.get("key", default="fallback")`
- Runtime updates: `config.set("key", value)` — update after load

**Non-functional:**
- Config source: in-memory dicts (extensible to files later)
- Thread-safety: bonus
- All lookups should be efficient

**Contract/API:**
```
ConfigManager():
  - get(key, default?) → value           # dot notation: "database.host"
  - set(key, value) → None               # runtime updates, triggers observers
  - load(config_dict) → None             # load/merge a config dict
  - load_env(env_name) → None            # apply environment overrides
  - on_change(key, callback) → None      # observer pattern
  - validate(schema) → list[str]         # returns list of validation errors
```

## Phase 2: Data Structure Choice

**Why nested dict?**
- Config is naturally hierarchical: database.host, database.port, api.timeout
- JSON/YAML/TOML all map to nested dicts
- Dot notation access = split on "." and walk the dict

**Dot notation traversal:**
```
"database.host" → split(".") → ["database", "host"]
→ config["database"] → {"host": "localhost", "port": 5432}
→ config["database"]["host"] → "localhost"
```

**Deep merge for environment overrides:**
```
base: {"database": {"host": "localhost", "port": 5432}}
prod: {"database": {"host": "prod-db.aws.com"}}
merged: {"database": {"host": "prod-db.aws.com", "port": 5432}}
         ↑ overridden                              ↑ inherited from base
```
- Shallow merge would replace entire "database" dict — we lose "port"
- Deep merge recursively merges nested dicts — keeps unoverridden keys

**Observer pattern for hot-reload:**
- Dict of `key → [list of callbacks]`
- On `set(key, value)`: fire all registered callbacks for that key
- Use `defaultdict(list)` to avoid KeyError on first registration

**Tradeoffs considered:**
- Could flatten all keys to dot notation internally (faster lookup)
  but loses the ability to get entire sections like `config.get("database")`
- Keeping nested dict preserves both capabilities

## Phase 3: Interface Design

**Classes and responsibilities:**
1. `ConfigStore` — Nested dict storage, dot notation get/set, deep merge
2. `ChangeNotifier` — Observer pattern, register callbacks, notify on change
3. `SchemaValidator` — Validate config values against expected types
4. `ConfigManager` — Public API, composes the above three

**Why separate?**
- ConfigStore can be used without observers (simpler use case)
- ChangeNotifier is reusable (shows up in Pub/Sub problem later)
- SchemaValidator is optional — not every config needs validation
- Each can be tested independently

## Phase 4: Core Implementation

**Build order:**
1. `ConfigStore` — dot notation get/set, deep merge, load
2. `ChangeNotifier` — observer registration and notification
3. `SchemaValidator` — type checking against schema
4. `ConfigManager` — compose all three, add environment support
5. Tests

**Key decisions:**
- (to be filled during implementation)

## Phase 5: Extensions

**What I added:**
- (to be filled)

**What I'd add with more time:**
- File-based config loading (JSON, YAML, TOML)
- Config freezing (make immutable after load)
- Thread-safety with threading.Lock
- Wildcard observers (listen to "database.*")
- Config diffing (show what changed between environments)

## Learnings
- Patterns used:
- Mistakes made:
- Time taken: