class Array:
    def __init__(self):
        self._row_len = 0
        self._data = []

    @property
    def rows(self):
        return len(self._data)

    def add_row(self, row: str):
        if self._row_len == 0:
            self._row_len = len(row)
        elif self._row_len != len(row):
            raise ValueError(f"invalid row length: {len(row)}, expected {self._row_len}")
        self._data.append(row)

    # (0,0) is top left, x grows horizontally to the right, y grows vertically down
    # for example in array below (2, 1) is A:
    # OOO
    # OOA
    # if x if larger than row_len, values are "repeated" (array grows infinitely to the right)
    def at(self, x: int, y: int):
        if x < 0 or y < 0 or y >= len(self._data):
            raise ValueError(f"invalid coordinates ({x}, {y}), allowed are x >= 0, 0 <= y < {len(self._data)}")
        return self._data[y][x % self._row_len]

    def __str__(self) -> str:
        return "\n".join(self._data)

    def count_trees(self, step_x: int, step_y: int) -> int:
        x, y = 0, 0
        trees_count = 0
        while y < self.rows:
            if self.at(x, y) == "#":
                trees_count += 1
            elif self.at(x, y) != ".":
                raise ValueError(f"incorrect input data at position ({x}, {y}): {self.at(x, y)}")
            x += step_x
            y += step_y
        return trees_count


def main():
    a = Array()
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                a.add_row(line)
    steps = [
        (1, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (1, 2),
    ]
    product = 1
    for s in steps:
        trees_count = a.count_trees(s[0], s[1])
        product *= trees_count
        print(f"trees encountered {s}: {trees_count}")
    print(f"total product: {product}")


if __name__ == "__main__":
    main()
