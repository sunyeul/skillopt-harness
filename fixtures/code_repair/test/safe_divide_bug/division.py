class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}

    def put(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return list(self.data.items())
