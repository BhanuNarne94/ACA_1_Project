from cache_functions import *
from utilities import *

Global.WAYS = WAYS
Global.LINE_CAPACITY = LINE_CAPACITY
Global.BYTE_SELECT = math.ceil(math.log2(LINE_CAPACITY / CPU_DATA_BUS))
Global.SETS = int(CACHE_CAPACITY / (WAYS * LINE_CAPACITY))
Global.INDEX_BITS = math.ceil(math.log2(Global.SETS))
Global.TAG_BITS = ADDRESS_BITS - Global.INDEX_BITS - Global.BYTE_SELECT


def testCacheModule():
    cache = Cache(sets=8, ways=8, test=True)
    if not cache.isCacheHit(address=64)[0]:
        cache.fillCacheLine(address=64)
    if not cache.isCacheHit(address=2097216)[0]:
        cache.fillCacheLine(address=2097216)
    if not cache.isCacheHit(address=4194368)[0]:
        cache.fillCacheLine(address=4194368)
    if not cache.isCacheHit(address=6291520)[0]:
        cache.fillCacheLine(address=6291520)
    if not cache.isCacheHit(address=8388672)[0]:
        cache.fillCacheLine(address=8388672)
    if not cache.isCacheHit(address=10485824)[0]:
        cache.fillCacheLine(address=10485824)
    if not cache.isCacheHit(address=12582976)[0]:
        cache.fillCacheLine(address=12582976)
    if not cache.isCacheHit(address=14680128)[0]:
        cache.fillCacheLine(address=14680128)
    if not cache.isCacheHit(address=4194368)[0]:
        cache.fillCacheLine(address=4194368)
    if not cache.isCacheHit(address=2097216)[0]:
        cache.fillCacheLine(address=2097216)
    if not cache.isCacheHit(address=25165888)[0]:
        cache.fillCacheLine(address=25165888)
        status = (4 == cache.getLine(address=25165888))
        print("Eviction Status", status)
    if not cache.isCacheHit(address=29360192)[0]:
        cache.fillCacheLine(address=29360192)
        status = (3 == cache.getLine(address=29360192))
        print("Eviction Status", status)
    cache.clearCache()


testCacheModule()
