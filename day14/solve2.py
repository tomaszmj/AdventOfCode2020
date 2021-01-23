class MemoryEmulator:
    def __init__(self):
        self._data = {}
        self._masklen = 36
        self._mask = "X" * self._masklen

    def write(self, address: int, value: int):
        new_address = ["X"] * self._masklen
        base_address_str = f'{address:036b}'
        for n, c in enumerate(self._mask):
            if c == "0":
                new_address[n] = base_address_str[n]
            elif c == "1":
                new_address[n] = "1"

        def _write(addr: str):
            self._data[int(addr, 2)] = value

        for_each_floating_address(''.join(new_address), _write)

    def set_mask(self, mask: str):
        if len(mask) != self._masklen:
            raise ValueError(f"invalid mask length, got {len(mask)}, expected 36")
        for c in mask:
            if c not in "X01":
                raise ValueError(f'invalid character in mask "{c}"')
        self._mask = mask

    def sum_values(self) -> int:
        return sum(self._data.values())


def for_each_floating_address(address: str, operation: callable):
    for n, c in enumerate(address):
        if c == "X":
            address0 = address[:n] + "0" + address[(n+1):]
            address1 = address[:n] + "1" + address[(n+1):]
            for_each_floating_address(address0, operation)
            for_each_floating_address(address1, operation)
            return
    operation(address)


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
