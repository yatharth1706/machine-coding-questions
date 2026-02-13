"""
LRU Cache — the main public API.

This is where HashMap + DoublyLinkedList come together.

OPERATIONS:
    get(key):
        1. Look up key in hashmap → O(1)
        2. If found: move node to head (mark as recently used) → O(1)
        3. Return value

    put(key, value):
        1. If key exists: update value + move to head → O(1)
        2. If new key and at capacity: evict tail → O(1)
        3. Create new node, add to head + hashmap → O(1)

    delete(key):
        1. Look up in hashmap → O(1)
        2. Remove from DLL → O(1)
        3. Remove from hashmap → O(1)

Everything is O(1). That's the whole point.
"""

from typing import Any, Optional
from doubly_linked_list import DoublyLinkedList
from models import Node

class LRUCache:
    """
    LRU Cache.
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self._map: dict[str, Node] = {}
        self._list = DoublyLinkedList()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        """
        if key not in self._map:
            return None
        node = self._map[key]
        self._list.move_to_head(node)
        return node.value
    
    def put(self, key: str, value: Any):
        """
        Put a value into the cache.
        """
        # Case 1: Key already exists — update value and move to head
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._list.move_to_head(node)
            return
        
        # Case 2: At capacity — evict LRU (tail node) before inserting
        if len(self._list) >= self.capacity:
            tail = self._list.remove_tail()
            del self._map[tail.key]
        
        # Case 3: New key — create node, add to head + map
        node = Node(key, value)
        self._list.add_to_head(node)
        self._map[key] = node
        
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        """
        if key not in self._map:
            return False
        node = self._map[key]
        self._list.remove(node)
        del self._map[key]
        return True
    
    def __len__(self) -> int:
        """
        Return the number of items in the cache.
        """
        return len(self._list)
    
    def __contains__(self, key: str) -> bool:
        """
            NEW CONCEPT — __contains__:
            Lets you write: if "key" in cache
            Without this, 'in' operator wouldn't work on your class.
        """
        return key in self._map
    
    def __repr__(self) -> str:
        """
        NEW CONCEPT — __repr__ vs __str__:
            __str__  → for end users, called by print()
            __repr__ → for developers, called in debugger/REPL
            If only one is defined, Python uses __repr__ as fallback for both.
        """
        return f"LRUCache(capacity={self.capacity}, size={len(self._list)}, items={self._list})"