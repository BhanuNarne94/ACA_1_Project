for outer in range(10000):
    address = 0
    for i in range(32):
        tag = i << 16
        address = hex(tag)[2:].zfill(8)
        print(f"0 {address}")
    counter = 0
    for i in range(32):
        counter += 1
        tag = (i << 16) | (33 << 6)
        address = hex(tag)[2:].zfill(8)
        print(f"0 {address}")
        if counter % 16 == 15:
            print(f"1 {address}")
            counter = 0
