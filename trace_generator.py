for outer in range(2):
    for inner in range(262144):
        address = hex(inner * 4)[2:].zfill(8)
        print(f"0 {address}")
