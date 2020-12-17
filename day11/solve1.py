from typing import List


OCCUPIED = "#"
EMPTY = "L"
FLOOR = "."


class Seat:
    def __init__(self, label: str):
        if label not in [OCCUPIED, EMPTY, FLOOR]:
            raise ValueError(f'invalid seat label "{label}"')
        self.label = label

    def occupied(self) -> int:
        if self.label == OCCUPIED:
            return 1
        return 0

    def new_label(self, occupied_neighbours: int) -> str:
        if self.label == EMPTY and occupied_neighbours == 0:
            return OCCUPIED
        if self.label == OCCUPIED and occupied_neighbours >= 4:
            return EMPTY
        return self.label


class Array:
    def __init__(self):
        self._row_len = 0
        self._data: List[List[Seat]] = []

    @property
    def rows(self):
        return len(self._data)

    @property
    def cols(self):
        return self._row_len

    def add_row(self, row: str):
        if self._row_len == 0:
            self._row_len = len(row)
        elif self._row_len != len(row):
            raise ValueError(f"invalid row length: {len(row)}, expected {self._row_len}")
        self._data.append(list(Seat(c) for c in row))

    # (0,0) is top left, x grows horizontally to the right, y grows vertically down
    # for example in array below (2, 1) is A:
    # OOO
    # OOA
    def at(self, x: int, y: int) -> Seat:
        if x < 0 or y < 0 or x >= self._row_len or y >= len(self._data):
            return Seat(FLOOR)
        return self._data[y][x]

    def count_occupied_neighbours(self, x: int, y: int) -> int:
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                count += self.at(x + dx, y + dy).occupied()
        return count

    def transform(self, destination) -> bool:
        array_changed = False
        for y in range(self.rows):
            for x in range(self.cols):
                seat = self.at(x, y)
                new_label = seat.new_label(self.count_occupied_neighbours(x, y))
                if new_label != seat.label:
                    array_changed = True
                destination.at(x, y).label = new_label
        return array_changed

    def count_all_occupied(self) -> int:
        occupied_count = 0
        for y in range(self.rows):
            for x in range(self.cols):
                occupied_count += self.at(x, y).occupied()
        return occupied_count


def main():
    arrays = [Array(), Array()]
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                arrays[0].add_row(line)
                arrays[1].add_row(line)
    i = 0
    while True:
        src = arrays[i % 2]
        dst = arrays[(i + 1) % 2]
        array_changed = src.transform(dst)
        i += 1
        if not array_changed:
            print(f"array stopped changing after {i} iterations, with {src.count_all_occupied()} seats occupied")
            return


if __name__ == "__main__":
    main()
