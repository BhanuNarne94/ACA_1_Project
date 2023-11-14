BYTE_SELECT = 6
INDEX_BITS = 15
TAG_BITS = 11


def addressDecomposition(address):
    byte_sel = address & ((2 ** BYTE_SELECT) - 1)
    # print("byte_sel", byte_sel)
    left_shift = ((2 ** INDEX_BITS) - 1) << BYTE_SELECT
    index_value = (address & left_shift) >> BYTE_SELECT
    # print("index_value", index_value)
    tag_left_shift = ((2 ** TAG_BITS) - 1) << (BYTE_SELECT + INDEX_BITS)
    tag_value = (address & tag_left_shift) >> (BYTE_SELECT + INDEX_BITS)
    # print(tag_value)
    all_values = {"tag": tag_value, "index": index_value, "byte": byte_sel}
    return all_values


def addressConstruction(address):
    print("Address", address)
    values = addressDecomposition(address)
    tag = values.get("tag")
    print("tag", tag)
    index = values.get("index")
    print("index", index)
    way_address = (tag << (INDEX_BITS + BYTE_SELECT)) + (index << BYTE_SELECT)    # ((1 << 6) >> )
    print(tag << (INDEX_BITS + BYTE_SELECT))
    print((index << BYTE_SELECT) >> BYTE_SELECT)
    print("way_address", way_address)


# addressConstruction(address=25165888)
# addressConstruction(address=12582976)
