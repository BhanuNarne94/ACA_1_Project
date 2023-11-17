

class CounterLru:
    def __init__(self, sets, ways):
        self.sets = sets
        self.ways = ways

    def updateLRU(self, set_num, way, cache_table):
        counter_list = cache_table[set_num]["counter"]
        if len(counter_list) == 0:
            counter_list.append(way)
            return
        elif way not in counter_list:
            counter_list.append(-1)
            for i in range(len(counter_list)-1, 0, -1):
                counter_list[i] = counter_list[i-1]
        elif way in counter_list:
            tag_index = counter_list.index(way)
            for i in range(tag_index, 0, -1):
                counter_list[i] = counter_list[i-1]
        counter_list[0] = way

    def evictLine(self, set_num, cache_table):
        new_way = cache_table[set_num]["counter"][-1]
        self.updateLRU(set_num, new_way, cache_table)
        return new_way



