class CounterLru:
    def __init__(self, ways):
        self.ways = ways
        self.access_order = [i for i in range(ways)]

    def updateLRU(self, line):
        """
        Update the LRU for the accessed cache line.
        :param line: The line that was accessed (0 to ways-1).
        """
        if line in self.access_order:
            self.access_order.remove(line)
        self.access_order.append(line)

    def evictLine(self):
        """
        Find and return the cache line to evict based on the LRU policy.
        :return: The index of the cache line to evict (0 to ways-1).
        """
        if len(self.access_order) > 0:
            ev=self.access_order.pop(0)
            self.access_order.append(ev)
            return ev
        return 0  # In case of an issue, return the first line as the least recently used

# Example usage:
# Create an LRU object with the number of ways (e.g., 8 for an 8-way set-associative cache)
# lru = LRU(8)
# To update LRU for a cache line, call lru.updateLRU(line)
# To evict a cache line based on LRU, call lru.evictLine()
