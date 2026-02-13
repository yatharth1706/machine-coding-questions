from lru_cache import LRUCache

class TestLRUCache:
    """
    Test the LRUCache class.
    """
    def test_put_and_get(self):
        cache = LRUCache(capacity=3)
        cache.put("a", 1)
        assert cache.get("a") == 1
        
    def test_update_existing_key(self):
        cache = LRUCache(capacity=3)
        cache.put("a", 1)
        cache.put("a", 2)
        assert cache.get("a") == 2
        
    def test_delete_existing_key(self):
        cache = LRUCache(capacity=3)
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None
        
    def test_delete_non_existing_key(self):
        cache = LRUCache(capacity=3)
        assert cache.delete("a") is False
        assert cache.get("a") is None

class TestLRUEviction:
    """Test that eviction removes the LEAST recently used item."""

    def test_evicts_oldest_when_full(self):
        cache = LRUCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict 'a'

        assert cache.get("a") is None  # Evicted
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_get_prevents_eviction(self):
        """Accessing a key should make it 'recently used' and protect it from eviction."""
        cache = LRUCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")       # 'a' is now most recently used
        cache.put("c", 3)    # Should evict 'b', NOT 'a'

        assert cache.get("a") == 1   # Protected by the get()
        assert cache.get("b") is None  # Evicted
        assert cache.get("c") == 3

    def test_put_update_prevents_eviction(self):
        """Updating a key should also protect it from eviction."""
        cache = LRUCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)   # Update 'a' — now most recently used
        cache.put("c", 3)    # Should evict 'b', NOT 'a'

        assert cache.get("a") == 10
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_multiple_evictions(self):
        cache = LRUCache(capacity=1)
        cache.put("a", 1)
        cache.put("b", 2)  # Evicts 'a'
        cache.put("c", 3)  # Evicts 'b'

        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") == 3


class TestLRUDunderMethods:
    """Test Python magic methods work correctly."""

    def test_len(self):
        cache = LRUCache(capacity=3)
        assert len(cache) == 0
        cache.put("a", 1)
        assert len(cache) == 1
        cache.put("b", 2)
        assert len(cache) == 2

    def test_contains(self):
        cache = LRUCache(capacity=3)
        cache.put("a", 1)
        assert "a" in cache
        assert "b" not in cache

    def test_capacity_validation(self):
        try:
            LRUCache(capacity=0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestLRUStats:
    """Test cache statistics tracking."""

    def test_hit_miss_counting(self):
        cache = LRUCache(capacity=3)
        cache.put("a", 1)
        cache.get("a")        # Hit
        cache.get("b")        # Miss
        cache.get("a")        # Hit

        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1

    def test_eviction_counting(self):
        cache = LRUCache(capacity=1)
        cache.put("a", 1)
        cache.put("b", 2)  # 1 eviction
        cache.put("c", 3)  # 2 evictions

        assert cache.stats()["evictions"] == 2