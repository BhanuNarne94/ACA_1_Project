from utilities import addressDecomposition, SETS, WAYS
from cache_functions import *


class Simulation(Cache):
    def __init__(self, sets, ways):
        super().__init__(sets, ways)
        print("Cache table", self.cache_table)

    def getTag(self, address=None):
        if address is not None:
            all_values = addressDecomposition(address)
            mem_address_tag = all_values.get("tag")
            mem_address_index = all_values.get("index")
            print("Byte Select: ", all_values.get("byte"))
            print("Index: ", all_values.get("index"))
            print("Tag: ", all_values.get("tag"))
        else:
            print("Address is None")
        print("\n********* After Cache Initialization **********")
        for idx, line in enumerate(self.cache_table[mem_address_index]["lines"]):
            print("line at way-{}: {}".format(idx, line))
        if not cache.isCacheHit(address)[0]:
            cache.fillCacheLine(address)
        # self.cache_table[mem_address_index]["lines"][idx]["state"] = 'E'
        print("\n********* After filling a cache line for address - {} **********".format(address))
        for idx, line in enumerate(self.cache_table[mem_address_index]["lines"]):
            print("Tag at way-{}: {}".format(idx, line.get("tag")))


cache = Simulation(sets=2, ways=8)
# cache.getTag(address=int("A00020", 16))
