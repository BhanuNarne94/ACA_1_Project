

class CounterLru:
    def __init__(self, sets, ways):
        self.sets = sets
        self.ways = ways
        self.list = []

    def updateLRU(self, set_num, way, cache_table):
        if len(self.list) == 0:
            self.list.append(way)
        elif way not in self.list:
            self.list.append(-1)
        for i in range(len(self.list)-1, -1, 0):
            if i == 0:
                break
            self.list[i] = self.list[i-1]
        self.list[0] = way
        for idx, line in enumerate(cache_table[set_num]["lines"]):
            # print("line -10 true LRU", idx)
            if idx < way:
                cache_table[set_num]["lines"][idx]["counter"] += 1
        cache_table[set_num]["lines"][way]["counter"] = 0

    def evictLine(self, set_num, cache_table):
        max_way = 0
        way = 0
        for _way, line in enumerate(cache_table[set_num]["lines"]):
            if line.get("counter") > max_way:
                max_way = line.get("counter")
                way = _way
        return way



