from cache_functions import Cache
from utilities import BusOp, SnoopResult, MessageToL1, Global, addressDecomposition, \
    messageToCache, Commands, busOperation
from tabulate import tabulate


class InputCommands(Cache):
    """
    This class is used to compare the input commands and on match corresponding command execution is made
    Also, it inherits the Cache class and uses the functions as needed
    """

    def __init__(self, sets, ways):
        super().__init__(sets, ways)

    def cpuRead(self, address, mem_address_index):
        """
        Simulate the behavior of a L2 cache when a READ request is received from its CPU
        :param address: trace file address
        :param mem_address_index: set number deduced from the address
        :return:
        """
        self.read_count = self.read_count + 1
        tag_hit_status, way = self.isCacheHit(address)
        if tag_hit_status == 1:
            self.cache_hit_count = self.cache_hit_count + 1
        if tag_hit_status == 0:  # on cache miss
            self.cache_miss_count = self.cache_miss_count + 1
            way = self.fillCacheLine(address)
            if Global.REPLACEMENT_POLICY == "plru":
                snoop_result = busOperation(BusOp.READ, address)
                if snoop_result == 'HIT' or snoop_result == 'HITM':
                    self.cache_table[mem_address_index]["lines"][way]["state"] = 'S'
                else:
                    self.cache_table[mem_address_index]["lines"][way]["state"] = 'E'
                messageToCache(MessageToL1.SENDLINE, address)

    def cpuWrite(self, address, mem_address_index):
        """
        Simulate the behavior of a L2 cache when a WRITE request is received from its CPU
        :param address: trace file address
        :param mem_address_index: set number deduced from the address
        :return:
        """
        self.write_count = self.write_count + 1
        tag_hit_status, way = self.isCacheHit(address)
        if tag_hit_status == 1:  # on cache hit
            self.cache_hit_count = self.cache_hit_count + 1
            if Global.REPLACEMENT_POLICY == "plru":
                line_state = self.cache_table[mem_address_index]["lines"][way]["state"]
                if line_state == 'S':
                    self.cache_table[mem_address_index]["lines"][way]["state"] = 'M'
                    busOperation(BusOp.INVALIDATE, address, expect_result=False)
                elif line_state == 'E':
                    self.cache_table[mem_address_index]["lines"][way]["state"] = 'M'
        if tag_hit_status == 0:  # on cache miss
            self.cache_miss_count = self.cache_miss_count + 1
            way = self.fillCacheLine(address)
            if Global.REPLACEMENT_POLICY == "plru":
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'M'
                busOperation(BusOp.RWIM, address, expect_result=False)
                messageToCache(MessageToL1.SENDLINE, address)

    def snoopedInvalidate(self, address, mem_address_index):
        """
        Simulate the behavior of a L2 cache that snooped a Bus Upgrade or Invalidate
        :param address: trace file address
        :param mem_address_index: set number deduced from the address
        :return:
        """
        tag_hit_status, way = self.isCacheHit(address)
        if tag_hit_status == 1:  # on cache hit
            line_state = self.cache_table[mem_address_index]["lines"][way]["state"]
            if line_state == 'S':
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'I'
                messageToCache(MessageToL1.INVALIDATELINE, address)

    def snoopedRead(self, address, mem_address_index):
        """
        Simulate the behavior of L2 cache that snooped a Processor READ
        :param address: trace file address
        :param mem_address_index: set number deduced from the address
        :return:
        """
        tag_hit_status, way = self.isCacheHit(address)
        if tag_hit_status == 1:  # on cache hit
            line_state = self.cache_table[mem_address_index]["lines"][way]["state"]
            if line_state == 'M':
                putSnoopResult(address, SnoopResult.HITM)
                messageToCache(MessageToL1.GETLINE, address)
                busOperation(BusOp.WRITE, address, expect_result=False)
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'S'
            elif line_state == 'E':
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'S'
                putSnoopResult(address, SnoopResult.HIT)
            elif line_state == 'S':
                putSnoopResult(address, SnoopResult.HIT)
        if tag_hit_status == 0:
            putSnoopResult(address, SnoopResult.NOHIT)

    def snoopedWrite(self, address, mem_address_index):
        pass

    def snoopedRWIM(self, address, mem_address_index):
        """
        Simulate the behavior of L2 cache that snooped Read for ownership (RWIM)
        :param address: trace file address
        :param mem_address_index: set number deduced from the address
        :return:
        """
        tag_hit_status, way = self.isCacheHit(address)
        if tag_hit_status == 1:
            line_state = self.cache_table[mem_address_index]["lines"][way]["state"]
            if line_state == 'M':
                putSnoopResult(address, SnoopResult.HITM)
                messageToCache(MessageToL1.GETLINE, address)
                busOperation(BusOp.WRITE, address, expect_result=False)
                messageToCache(MessageToL1.INVALIDATELINE, address)
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'I'
            elif line_state == 'E':
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'I'
                messageToCache(MessageToL1.INVALIDATELINE, address)
            elif line_state == 'S':
                self.cache_table[mem_address_index]["lines"][way]["state"] = 'I'
                messageToCache(MessageToL1.INVALIDATELINE, address)

    def printValidLine(self):
        """
        Print the contents and state of each valid line in the cache
        :return:
        """
        if Global.REPLACEMENT_POLICY == "plru":
            print("\n************** Contents of Valid Lines in L2 Cache ***************")
            current_index = []
            for set_idx, index in enumerate(self.cache_table):
                for idx, line in enumerate(index["lines"]):
                    if not line.get("state") == 'I':
                        each_line = [line.get("state"), line.get("tag"), set_idx, idx,
                                     line.get("lru"), index["lru_bits"]]
                        current_index.append(each_line)
            #print(tabulate(current_index, headers=["State", "Tag", "Set", "Way",
            #                                       "LRU bits", "LRU bits per set"], tablefmt="fancy_grid"))

    def commandOperations(self, command, address=None):
        """
        This function accepts the input commands and on a match routes to the respective command
        function for the execution
        :param command:
        :param address:
        :return:
        """
        if address is not None:
            addr_values = addressDecomposition(address)
            mem_address_index = addr_values.get("index")
        """
        Code to execute READ request from the processor
        """
        if command == Commands.CPU_READ.value or command == Commands.CPU_INSTRUCTION_READ.value:
            self.cpuRead(address, mem_address_index)
        """
        Code to execute WRITE request from the processor
        """
        if command == Commands.CPU_WRITE.value:
            self.cpuWrite(address, mem_address_index)
        """
        Code to execute snooped invalidate command
        """
        if command == Commands.SNOOPED_INVALIDATE.value:
            self.snoopedInvalidate(address, mem_address_index)
        """
        Code to execute snooped read command
        """
        if command == Commands.SNOOPED_READ.value:
            self.snoopedRead(address, mem_address_index)
        """
        Code to execute snooped write command
        """
        if command == Commands.SNOOPED_WRITE.value:
            self.snoopedWrite(address, mem_address_index)
        """
        Code to execute snooped write command
        """
        if command == Commands.SNOOPED_RWIM.value:
            self.snoopedRWIM(address, mem_address_index)
        """
        Code to execute Clear cache command
        """
        if command == Commands.CLEAR_CACHE.value:
            self.clearCache()
        """
        Code to execute Print contents and state of a valid line command
        """
        if command == Commands.PRINT_VALID_LINE.value:
            self.printValidLine()


def putSnoopResult(address, snoop_result):
    """
    Report the result of our snooping bus operations performed by other caches
    :param address: trace file address
    :param snoop_result: The intended snoop result to be posted based on the line's state and the command
    :return:
    """
    if Global.mode == 'n':
        print("SnoopResult: Address {}, SnoopResult: {}".format(hex(address), snoop_result.name))
