import math
import argparse
import os.path
import sys

from enum import Enum

filename = None

# Cache Parameters
DEBUG = 0
CACHE_CAPACITY = 16 * (2 ** 20) * 8  # 16MB cache
LINE_CAPACITY = 64 * 8  # 64 byte cache line
WAYS = 8  # 8 way set associative
ADDRESS_BITS = 32  # Cache Address bits
CPU_DATA_BUS = 8  # CPU is a byte addressable


class Global:
    mode = 's'
    LINE_CAPACITY = LINE_CAPACITY
    WAYS = WAYS
    SETS = None
    BYTE_SELECT = None
    INDEX_BITS = None
    TAG_BITS = None
    REPLACEMENT_POLICY = None


PSEUDO_LRU = WAYS - 1
command_size = 4
address_size = 32


# for DC replacement policy
DC_GROUP1_LOWER = 0
DC_GROUP1_UPPER = 2 * Global.WAYS
DC_GROUP2_UPPER = 4 * Global.WAYS


# Bus operation Types
class BusOp(Enum):
    READ = 1
    WRITE = 2
    INVALIDATE = 3
    RWIM = 4


# Snoop Result Types
class SnoopResult(Enum):
    HIT = 0
    HITM = 1
    NOHIT = 2


# L2 to L1 Message Types
class MessageToL1(Enum):
    GETLINE = 1
    SENDLINE = 2
    INVALIDATELINE = 3
    EVICTLINE = 4


# Input Commands
class Commands(Enum):
    CPU_READ = 0
    CPU_WRITE = 1
    CPU_INSTRUCTION_READ = 2
    SNOOPED_INVALIDATE = 3
    SNOOPED_READ = 4
    SNOOPED_WRITE = 5
    SNOOPED_RWIM = 6
    CLEAR_CACHE = 8
    PRINT_VALID_LINE = 9


def addressDecomposition(address):
    """
    Decomposes the input address into tag, index and byte-select values
    :param address: trace file address
    :return: decomposed tag, index and byte select values
    """
    byte_sel = address & ((2 ** Global.BYTE_SELECT) - 1)
    left_shift = ((2 ** Global.INDEX_BITS) - 1) << Global.BYTE_SELECT
    index_value = (address & left_shift) >> Global.BYTE_SELECT
    tag_left_shift = ((2 ** Global.TAG_BITS) - 1) << (Global.BYTE_SELECT + Global.INDEX_BITS)
    tag_value = (address & tag_left_shift) >> (Global.BYTE_SELECT + Global.INDEX_BITS)
    all_values = {"tag": tag_value, "index": index_value, "byte": byte_sel}
    return all_values


def parseArguments():
    """
    Parse the command line arguments and get the file name, mode and other user defined parameters
    :return:
    """
    parser = argparse.ArgumentParser(description="Parsing command line arguments for user input")
    parser.add_argument('file_name', nargs='?', type=str)
    parser.add_argument('-m', '--mode', nargs='?', type=str,
                        help="Mode of running. For silent mode: s, For normal mode: n (default: s)")
    parser.add_argument('-s', '--sets', nargs='?', type=int,
                        help="Total number of sets")
    parser.add_argument('-a', '--associativity', nargs='?', type=int,
                        help="set-associativity")
    parser.add_argument('-b', '--bytes', nargs='?', type=int,
                        help="Number of bytes per line")
    parser.add_argument('-rp', '--replacement_policy', nargs='?', type=str,
                        help="Replacement Policy to use. For LRU: truelru, for Pseudo LRU: plru and for DC "
                             "replacement: dcrp")
    args = parser.parse_args()
    if vars(args).get('file_name') is None:
        print("****ERROR : No valid inputs passed. use python main.py -h for more information")
        sys.exit(1)
    if args.replacement_policy is not None:
        Global.REPLACEMENT_POLICY = args.replacement_policy
    if args.mode is not None:
        Global.mode = args.mode
    try:
        if args.bytes is None and args.sets is None and args.associativity is None:
            if Global.mode == 'n':
                raise Exception("")
        if args.bytes is not None and math.log2(args.bytes).is_integer():
            if args.sets is not None and math.log2(args.sets).is_integer():
                if args.associativity is not None and math.log2(args.associativity).is_integer() \
                        and args.associativity <= 32:
                    Global.LINE_CAPACITY = args.bytes
                    Global.WAYS = args.associativity
                    Global.SETS = args.sets
                    Global.BYTE_SELECT = math.ceil(math.log2(Global.LINE_CAPACITY))
                    if (Global.BYTE_SELECT + math.log2(Global.SETS) + (2 * math.log2(Global.WAYS))) \
                            > ADDRESS_BITS:
                        raise Exception("Cache cannot be formed with the given parameters, "
                                        "so proceeding with the default values")
                else:
                    raise Exception("Cache cannot be formed with the given parameters, "
                                    "so proceeding with the default values")
            else:
                raise Exception("Cache cannot be formed with the given parameters, "
                                "so proceeding with the default values")
        else:
            raise Exception("Cache cannot be formed with the given parameters, "
                            "so proceeding with the default values")
    except Exception as e:
        if not len(e.args[0]) == 0:
            if Global.mode == 'n':
                print(e)
        Global.WAYS = WAYS
        Global.LINE_CAPACITY = LINE_CAPACITY
        Global.BYTE_SELECT = math.ceil(math.log2(LINE_CAPACITY / CPU_DATA_BUS))
        Global.SETS = int(CACHE_CAPACITY / (WAYS * LINE_CAPACITY))
    finally:
        Global.INDEX_BITS = math.ceil(math.log2(Global.SETS))
        Global.TAG_BITS = ADDRESS_BITS - Global.INDEX_BITS - Global.BYTE_SELECT
    global filename
    filename = args.file_name


def readFile():
    """
    Check if the file exits or not. If exists, open the file in the read_output mode
    :return: file handler
    """
    if not os.path.exists(filename):
        print("****ERROR: File mentioned doesn't exist")
        sys.exit(1)
    else:
        file_handle = open(filename, 'r')
    return file_handle


def getNextCommand(line):
    """
    Read the file line by line and get the valid command and address
    :return: command and address
    """
    my_tuple = tuple()
    if line is not None:
        line = line.strip()
        my_tuple = line.split(" ")
    if len(my_tuple) != 2:
        if len(my_tuple) == 1:
            value = my_tuple[0].strip()
            if len(value) > 0 and (int(value) == Commands.PRINT_VALID_LINE.value
                                   or int(value) == Commands.CLEAR_CACHE.value):
                if Global.mode == 'v':
                    print("Command :{}:{}".format(value, Commands(value).name))
                return int(value), None
            elif value == '':
                return None, None
            else:
                if Global.mode == 'n':
                    print("Address is found without any valid command")
                return None, None
        else:
            if Global.mode == 'n':
                print("**** ERROR : Expecting only command and address (2 values), but found invalid number of values")
            return None, None
    else:
        n, address = my_tuple[0].strip(), my_tuple[1].strip()
        if len(address) > 8:
            address = None
        address = getHexValue(address)
        if address is None:
            return None, None
        return int(n), address


def getHexValue(address_str):
    """
    Convert the address string parameter into hexadecimal value and return the hexadecimal address
    :param address_str: trace file address
    :return: address in hexadecimal format
    """
    value = None
    try:
        value = int(address_str, 16)
    except:
        return
    finally:
        return value


def messageToCache(message, address):
    """
    Used to simulate communication to our upper level cache
    :param message: message to be sent to L1
    :param address: address to be passed to L1
    :return:
    """
    if Global.mode == 'n':
        print("L2: {}   {}".format(message.name, hex(address)))


def getSnoopResult(address):
    """
    Simulate the reporting of snoop results by other caches
    :param address: trace file address
    :return:
    """
    snoop_bits = address & 3
    if snoop_bits == 0:
        snoop_outcome = SnoopResult(0).name
    elif snoop_bits == 1:
        snoop_outcome = SnoopResult(1).name
    else:
        snoop_outcome = SnoopResult(2).name
    return snoop_outcome


def busOperation(bus_op, address, expect_result=True):
    """
    Used to simulate a bus operation and to capture the snoop results of last level
    caches of other processors
    :param bus_op: Operation to be sent on bus as a result of processor request
    :param address: trace file address
    :param expect_result: True for Processor READ and False for th remaining commands
    :return:
    """
    snoop_result = getSnoopResult(address)
    if Global.mode == 'n':
        if expect_result:
            print("BusOperation: {}, Address: {}, SnoopResult: {}".format(bus_op.name, hex(address), snoop_result))
            return snoop_result
        else:
            print("BusOperation: {}, Address: {}".format(bus_op.name, hex(address)))
