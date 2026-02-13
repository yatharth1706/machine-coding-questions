## In-Memory Cache (LRU / LFU) - Thought Process

### Phase 1 - Clarify Requirements
**Functional:**
- Operations: get(key), put(key, value), delete(key)
- Eviction policy (LRU first, LFU as extension)
- TTL (Time to live) support as bonus
- Cache miss returns None
- Generic key value types

**Non-functional:**
- All operations should be fast O(1)
- In-memory, single process
- Thread-safety as bonus
- Cache stats (hits, misses, eviction count) as bonus

**Contract/API:**
```
Cache(capacity):
    - get(key) -> value | None      # O(1)
    - put(key, value, ttl?)         # O(1)
    - delete(key)                   # O(1)
    - Eviction: LRU (Least recently used)
    - Optional: TTL, stats, thread-safety
```

## Phase 2: Data Structure Choice
**Why HashMap + Doubly Linked List?**
- Hashmap alone: O(1) lookup but no ordering
- Array/List alone: ordering is there but no fast lookup O(n) find + move
- Combined: Hashmap O(1) lookup, DLL gives O(1) reorder
- Hashmap stores: key -> node reference
- DLL maintains access order - Most recent at head and least recent at tail

**Visual:**
```
Most Recent                          Least Recent
   HEAD ↔ [A] ↔ [B] ↔ [C] ↔ [D] ↔ TAIL
                                      ↑ evict this
```

**Tradeoffs considered:**
- `collections.OrderedDict` is a shortcut but interviewers want to see the manual approach
- Could use singly linked list but removal would be O(n) — need doubly for O(1) removal

## Phase 3: Interface Design:
**Classes and responsibilities:**
1. `Node` — Data container (key, value, prev, next pointers)
2. `DoublyLinkedList` — Ordering logic (add_to_head, remove, move_to_head, remove_tail)
3. `LRUCache` — Public API, owns hashmap + linked list

**Why separate DLL from Cache?**
- Reusable (needed for LFU too)
- Separation of concerns — cache logic stays clean
- Easier to test independently

## Phase 4: Core Implementation

**Build order:**
1. `Node` dataclass
2. `DoublyLinkedList` with add/remove/move operations
3. `LRUCache` with `get` and `put`
4. Manual testing with examples

**Key decisions:**
- (to be filled during implementation)

## Phase 5: Extensions

**What I added:**
- (to be filled)

**What I'd add with more time:**
- TTL support (lazy expiration on access)
- Cache stats (hit/miss counters)
- Thread-safety with `threading.Lock`
- LFU as alternate policy using Strategy pattern