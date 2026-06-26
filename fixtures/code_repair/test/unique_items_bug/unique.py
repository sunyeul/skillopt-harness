class StablePriorityQueue:
    def __init__(self):
        self.items = []

    def push(self, item, priority):
        self.items.append((priority, item))

    def pop(self):
        priority, item = min(self.items)
        self.items.remove((priority, item))
        return item

    def remove(self, item):
        return False
