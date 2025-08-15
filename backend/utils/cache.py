import time

class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self.store = {}

    def get(self, key):
        v = self.store.get(key)
        if not v:
            return None
        val, exp = v
        if time.time() > exp:
            self.store.pop(key, None)
            return None
        return val

    def set(self, key, value):
        self.store[key] = (value, time.time() + self.ttl)
