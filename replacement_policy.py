import math
UP = 0
DOWN = 1


class PseudoLRU:
    def __init__(self, way):
        self.way = way
        self.root = PseudoLRU.create_node(0, way - 1)
        if way > 1:
            self.root = PseudoLRU.addLink(self.root, 0, self.way - 1)

    @staticmethod
    def create_node(lower_limit, upper_limit):
        """
        Creates a node with the lower and upper limit parameters
        :param lower_limit
        :param upper_limit
        :return:
        """
        return PseudoLRUBit(lower_limit, upper_limit)

    @staticmethod
    def addLink(element, lower, upper):
        """
        Used to link the nodes created using create_node() method
        :param element
        :param lower
        :param upper
        :return:
        """
        if lower < upper:
            mid = math.floor((upper + lower) / 2)
            up = PseudoLRU.create_node(lower, mid)
            down = PseudoLRU.create_node(mid + 1, upper)
            element.up = PseudoLRU.addLink(up, lower, mid)
            element.down = PseudoLRU.addLink(down, mid + 1, upper)
        else:
            return None
        return element

    def updateLRU(self, line):
        """
        Update the LRU for way that is in use by using pseudo-LRU scheme
        :param line: line to which LRU needs to be updated
        :return: lru bits
        """
        lru = ""
        if line < 0 or line >= self.way:
            print("This is {}-way set associative, permitted lines are 0 to {} but given {} as the line"
                  .format(self.way, self.way - 1, line))
        current = self.root
        while True:
            if current.up is None or current.down is None:
                if line == current.upper_limit:
                    current.bit = DOWN
                    if self.way > 1:
                        lru = lru + str(current.bit)
                else:
                    current.bit = UP
                    if self.way > 1:
                        lru = lru + str(current.bit)
                break
            mid = (current.upper_limit + current.lower_limit) / 2
            if line > mid:
                current.bit = DOWN
                if self.way > 1:
                    lru = lru + str(current.bit)
                current = current.down
            else:
                current.bit = UP
                if self.way > 1:
                    lru = lru + str(current.bit)
                current = current.up
        return lru

    def evictLine(self):
        """
        Used to evict a line using the pseudo-LRU scheme
        :return: evicted line way and lru
        """
        lru = ""
        current = self.root
        while True:
            if current.up is None or current.down is None:
                if current.bit == UP:
                    current.bit = DOWN
                    line = current.upper_limit
                    if self.way > 1:
                        lru = lru + str(current.bit)
                else:
                    current.bit = UP
                    line = current.lower_limit
                    if self.way > 1:
                        lru = lru + str(current.bit)
                break

            if current.bit == UP:
                current.bit = DOWN
                if self.way > 1:
                    lru = lru + str(current.bit)
                current = current.down
            else:
                current.bit = UP
                if self.way > 1:
                    lru = lru + str(current.bit)
                current = current.up
        return line, lru


class PseudoLRUBit:
    """
    Creates an instance for every node
    """
    def __init__(self, lower, upper):
        self.bit = 0
        self.up = None
        self.down = None
        self.upper_limit = upper
        self.lower_limit = lower

