class CounterLru:
    def __init__(self, ways):
        self.ways = ways
        # self.access_order = [i for i in range(ways)]

    def updateLRU(self, set_num, way, cache_table):
        if way in cache_table[set_num]["counter"]:
            cache_table[set_num]["counter"].remove(way)
        cache_table[set_num]["counter"].append(way)

    def evictLine(self, set_num, cache_table):
        if len(cache_table[set_num]["counter"]) > 0:
            ev = cache_table[set_num]["counter"].pop(0)
            cache_table[set_num]["counter"].append(ev)
            return ev
        return 0  # In case of an issue, return the first line as the least recently used

# Example usage:
# Create an LRU object with the number of ways (e.g., 8 for an 8-way set-associative cache)
# lru = LRU(8)
# To update LRU for a cache line, call lru.updateLRU(line)
# To evict a cache line based on LRU, call lru.evictLine()