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
        