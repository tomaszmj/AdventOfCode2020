class MemoryEmulator:
    def __init__(self):
        self._data = {}
        self._masklen = 36
        self._mask = "X" * self._masklen

    def write(self, address: int, value: int):
        new_value = 0
        for n, c in enumerate(self._mask):
            bitmask = 1 << (self._masklen - n - 1)
            if c == "X":
                new_value += value & bitmask
            elif c == "1":
                new_value += bitmask
        self._data[address] = new_value

    def set_mask(self, mask: str):
        if len(mask) != self._masklen:
            raise ValueError(f"invalid mask length, got {len(mask)}, expected 36")
        for c in mask:
            if c not in "X01":
                raise ValueError(f'invalid character in mask "{c}"')
        self._mask = mask

    def sum_values(self) -> int:
        return sum(self._data.values())


def main():
    memory = MemoryEmulator()
    with open("data.txt") as f:
        for line in f:
            try:
                line = line.strip()
                value = line.split("=")[1][1:]
                if line[:3] == "mem":
                    address = int(line[4:line.find("]")])
                    memory.write(address, int(value))
                elif line[:4] == "mask":
                    memory.set_mask(value)
                else:
                    raise ValueError("unexpected input line")
            except (ValueError, IndexError) as e:
                print(f'error parsing "{line}": {e}')
                return
    print(memory.sum_values())


if __name__ == "__main__":
    main()
