from tabulate import tabulate

from replacement_policy import PseudoLRU
from utilities import addressDecomposition, Global, messageToCache, MessageToL1, busOperation, BusOp
from dc_replacement import DuelingClock
from counter_lru_replacement import CounterLru


class Cache:
    """
    This class holds all the function related to the Cache
    """

    def __init__(self, sets, ways, test=None):
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        self.read_count = 0
        self.write_count = 0
        self.cache_table = None
        self.find_lru = None
        self.ways = ways
        self.sets = sets
        self.test = test
        self.policy_select = 0
        self.dualing_clock = DuelingClock(sets, ways)
        self.counter_lru = CounterLru(ways)
        # Initialisation code starts here
        set_index = []
        for index in range(sets):
            lines = []
            if Global.REPLACEMENT_POLICY == "plru":
                for line in range(ways):
                    each_line = {"state": 'I', "tag": None, "lru": ""}
                    lines.append(each_line)
                index_lru = PseudoLRU(ways)
                tag_array = {
                    "pLRU": index_lru,
                    "lines": lines,
                    "lru_bits": ""
                }
                set_index.append(tag_array)
            elif Global.REPLACEMENT_POLICY == "dcrp":
                for line in range(ways):
                    each_line = {"state": 'I', "tag": None, "hit_bit": 0}
                    lines.append(each_line)
                tag_array = {
                    "replace_ptr": 0,
                    "lines": lines
                }
                set_index.append(tag_array)
            elif Global.REPLACEMENT_POLICY == "truelru":
                for line in range(ways):
                    each_line = {"state": 'I', "tag": None}
                    lines.append(each_line)
                tag_array = {
                    "counter": [],
                    "lines": lines
                }
                set_index.append(tag_array)
        self.cache_table = set_index

    def clearCache(self):
        """
        Clears the cache or resets all the cache lines
        :return:
        """
        for index in self.cache_table:  # todo: write for different policies
            lines = []
            for line in index["lines"]:
                if not line["state"] == 'I':
                    line["state"] = 'I'
                    line["tag"] = None
                    line["lru"] = ""
            index_lru = PseudoLRU(self.ways)
            index["pLRU"] = index_lru
            index["lru_bits"] = ""
        if Global.mode == 'n':
            print("Cleared cache")

    def isCacheHit(self, address):
        """
        Used to determine if there is a cache hit
        :param address: trace file address
        :return: tag hit status and way for a particular line in the set
        """
        tag_hit = 0
        way = None
        addr_values = addressDecomposition(address)
        mem_address_tag = addr_values.get("tag")
        mem_address_index = addr_values.get("index")
        for idx, line in enumerate(self.cache_table[mem_address_index]["lines"]):
            if line.get("tag") == mem_address_tag and not line.get("state") == 'I':
                tag_hit = 1
                way = idx
                if Global.REPLACEMENT_POLICY == "plru":
                    line["lru"] = self.cache_table[mem_address_index]["pLRU"].updateLRU(idx)
                    self.cache_table[mem_address_index]["lru_bits"] = line["lru"]
                elif Global.REPLACEMENT_POLICY == "dcrp":
                    self.cache_table[mem_address_index]["lines"][way]["hit_bit"] = 1
                elif Global.REPLACEMENT_POLICY == "truelru":
                    self.counter_lru.updateLRU(mem_address_index, way, self.cache_table)
                break
        return tag_hit, way

    def fillCacheLine(self, address):
        """
        Used to fill the cache line on a cache miss. Also uses updateLRU and evictLine() functions
        :param address: trace file address
        :return: way for a particular line in the set
        """
        addr_values = addressDecomposition(address)
        mem_address_tag = addr_values.get("tag")
        mem_address_index = addr_values.get("index")
        if Global.REPLACEMENT_POLICY != "dcrp":
            any_empty_line = 0
            for idx, line in enumerate(self.cache_table[mem_address_index]["lines"]):
                if line.get("state") == 'I':
                    any_empty_line = 1
                    line["tag"] = mem_address_tag
                    way = idx
                    if Global.REPLACEMENT_POLICY == "plru":
                        line["lru"] = self.cache_table[mem_address_index]["pLRU"].updateLRU(idx)
                        self.cache_table[mem_address_index]["lru_bits"] = line["lru"]
                    elif Global.REPLACEMENT_POLICY == "truelru":
                        self.counter_lru.updateLRU(mem_address_index, way, self.cache_table)
                        self.cache_table[mem_address_index]["lines"][way]["state"] = 'V'
                    break
            if not any_empty_line == 1:
                if Global.REPLACEMENT_POLICY == "plru":
                    way, lru = self.cache_table[mem_address_index]["pLRU"].evictLine()
                    self.cache_table[mem_address_index]["lines"][way]["lru"] = lru
                    self.cache_table[mem_address_index]["lru_bits"] = lru
                elif Global.REPLACEMENT_POLICY == "truelru":
                    way = self.counter_lru.evictLine(mem_address_index, self.cache_table)
                    # Todo: check if the above line is okay
                tag_at_way = self.cache_table[mem_address_index]["lines"][way]["tag"]
                way_address = (tag_at_way << (Global.INDEX_BITS + Global.BYTE_SELECT)) + \
                              (mem_address_index << Global.BYTE_SELECT)
                messageToCache(MessageToL1.EVICTLINE, way_address)
                if self.cache_table[mem_address_index]["lines"][way]["state"] == 'M':
                    busOperation(BusOp.WRITE, way_address, expect_result=False)
                self.cache_table[mem_address_index]["lines"][way]["tag"] = mem_address_tag
            if self.test:
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'S'
            return way
        elif Global.REPLACEMENT_POLICY == "dcrp":
            group = self.dualing_clock.determineSetGroup(mem_address_index)
            if group == "CLOCK":
                self.dualing_clock.clockAlgorithm(mem_address_index, mem_address_tag, self.cache_table)
            elif group == "SCAN":
                self.dualing_clock.scanAlgorithm(mem_address_index, mem_address_tag, self.cache_table)

    def outputStatistics(self):
        """
        Used to display all the output key statistics
        :return:
        """
        print("\n**************** Output Key Statistics ******************")
        try:
            cache_hit_ratio = round((self.cache_hit_count / (self.cache_hit_count + self.cache_miss_count)), 3)
            cache_miss_ratio = round((self.cache_miss_count / (self.cache_hit_count + self.cache_miss_count)), 3)
        except ZeroDivisionError:
            cache_hit_ratio = 0
            cache_miss_ratio = 0
        output_data = [[self.read_count, self.write_count, self.cache_hit_count, self.cache_miss_count,
                        (cache_hit_ratio * 100), (cache_miss_ratio * 100)]]
        print(tabulate(output_data, headers=["Cache Reads", "Cache Writes", "Cache Hit Count", "Cache Miss Count",
                                             "Cache Hit Ratio", "Cache Miss Ratio"], tablefmt="fancy_grid"))

    def getLine(self, address):
        """
        Created only for testing LRU separately
        :param address:
        :return:
        """
        addr_values = addressDecomposition(address)
        mem_address_tag = addr_values.get("tag")
        mem_address_index = addr_values.get("index")
        for idx, line in enumerate(self.cache_table[mem_address_index]["lines"]):
            if line.get("tag") == mem_address_tag:
                return idx
