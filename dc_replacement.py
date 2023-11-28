import math

from utilities import Global


class DuelingClock:
    def __init__(self, sets, ways):
        self.policy_select = 0
        self.sets = sets
        self.set_bits = int(math.log2(sets))
        self.ways = ways

    def determineSetGroup(self, set_num):
        msb = (self.policy_select >> (self.set_bits - 1)) & 1
        if (set_num >= Global.DC_GROUP1_LOWER) and (set_num < Global.DC_GROUP1_UPPER):
            self.policy_select -= 1
            # print("inside clock:{} ".format(set_num))
            return "CLOCK"
        elif (set_num >= Global.DC_GROUP1_UPPER) and (set_num < Global.DC_GROUP2_UPPER):
            self.policy_select += 1
            # print("inside scan: {}".format(set_num))
            return "SCAN"
        elif (set_num >= Global.DC_GROUP2_UPPER) and (set_num < self.sets):
            # print("inside g3: {}".format(set_num))
            if msb == 1:
                return "CLOCK"
            else:
                return "SCAN"

    def clockAlgorithm(self, mem_address_index, mem_address_tag, cache_table):
        cache_table[mem_address_index]["replace_ptr"] \
            = (cache_table[mem_address_index]["replace_ptr"] + 1) % self.ways
        way = cache_table[mem_address_index]["replace_ptr"]
        while cache_table[mem_address_index]["lines"][way]["hit_bit"] == 1:
            cache_table[mem_address_index]["lines"][way]["hit_bit"] = 0
            cache_table[mem_address_index]["replace_ptr"] \
                = (cache_table[mem_address_index]["replace_ptr"] + 1) % self.ways
            way = cache_table[mem_address_index]["replace_ptr"]
        way_to_replace = cache_table[mem_address_index]["replace_ptr"]
        cache_table[mem_address_index]["lines"][way_to_replace]["tag"] = mem_address_tag
        cache_table[mem_address_index]["lines"][way_to_replace]["state"] = 'V'

    def scanAlgorithm(self, mem_address_index, mem_address_tag, cache_table):
        # print("inside scan algorithm: ")
        way = cache_table[mem_address_index]["replace_ptr"]
        while cache_table[mem_address_index]["lines"][way]["hit_bit"] == 1:
            cache_table[mem_address_index]["lines"][way]["hit_bit"] = 0
            cache_table[mem_address_index]["replace_ptr"] \
                = (cache_table[mem_address_index]["replace_ptr"] + 1) % self.ways
            way = cache_table[mem_address_index]["replace_ptr"]
        way_to_replace = cache_table[mem_address_index]["replace_ptr"]
        cache_table[mem_address_index]["lines"][way_to_replace]["tag"] = mem_address_tag
        cache_table[mem_address_index]["lines"][way_to_replace]["state"] = 'V'
        # print(cache_table[mem_address_index]["lines"])
