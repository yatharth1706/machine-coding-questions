# 01 — In-Memory Cache (LRU)

## Problem Statement

Design and implement an in-memory cache with **Least Recently Used (LRU)** eviction policy where all operations are O(1).

## Requirements

| Operation | Description | Time Complexity |
|-----------|-------------|-----------------|
| `get(key)` | Retrieve value, return None on miss | O(1) |
| `put(key, value)` | Insert/update key-value pair | O(1) |
| `delete(key)` | Remove key, return True/False | O(1) |

- Fixed capacity — evicts LRU item when full
- Cache stats tracking (hits, misses, evictions, hit rate)
- Python magic methods: `len()`, `in` operator, `repr()`

## Run

```bash
# Demo
cd solution && python3 lru_cache.py

# Tests
cd tests && python3 -m pytest test_lru_cache.py -v
```