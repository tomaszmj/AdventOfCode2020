from typing import NamedTuple, Set, Iterable


ACTIVE = "#"
INACTIVE = "."


class Point(NamedTuple):
    x: int
    y: int
    z: int


# Euclidean pinates:
#   y
#   ^
#   |
#   --> x
#  /
# z
class Space:
    def __init__(self):
        self.lower = Point(0, 0, 0)
        self.upper = Point(-1, -1, -1)  # space is from lower to upper (inclusive), upper < lower indicates 0 size
        self.actives: Set[Point] = set()
        self.input_row_len = 0
        self.rows_added = 0

    def add_row(self, row: str):
        if self.input_row_len == 0:
            self.input_row_len = len(row)
        elif len(row) != self.input_row_len:
            raise ValueError(f"cannot add row, expected len {self.input_row_len}, got {len(row)}: {row}")
        z = 0
        y = -self.rows_added
        for x, field in enumerate(row):
            if field == ACTIVE:
                self.set_active(Point(x, y, z))
        self.rows_added += 1

    def get(self, p: Point) -> str:
        if p in self.actives:
            return ACTIVE
        return INACTIVE

    def set_active(self, p: Point):
        self.lower = Point(min(p.x, self.lower.x), min(p.y, self.lower.y), min(p.z, self.lower.z))
        self.upper = Point(max(p.x, self.upper.x), max(p.y, self.upper.y), max(p.z, self.upper.z))
        self.actives.add(p)

    def set_inactive(self, p: Point):
        if p in self.actives:
            # we do not modify lower/upper bounds here, as it is not necessary
            # (bounds are only to simplify iteration, space is infinite)
            self.actives.remove(p)

    def yield_all_points(self) -> Iterable[Point]:
        for z in range(self.lower.z, self.upper.z + 1, 1):
            for y in range(self.lower.y, self.upper.y + 1, 1):
                for x in range(self.lower.x, self.upper.x + 1, 1):
                    yield Point(x, y, z)

    def string(self, z: int) -> str:
        return "\n".join(
            "".join(self.get(Point(x, y, z)) for x in range(self.lower.x, self.upper.x + 1, 1))
            for y in range(self.upper.y, self.lower.y - 1, -1)
        )

    def count_active_neighbours(self, p: Point) -> int:
        count = 0
        for dz in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == dy == dz == 0:
                        continue
                    if self.get(Point(p.x + dx, p.y + dy, p.z + dz)) == ACTIVE:
                        count += 1
        return count

    def transform_to(self, dst):
        pass


def main():
    spaces = [Space(), Space()]
    with open("data_small.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                spaces[0].add_row(line)
                spaces[1].add_row(line)
    print(f"{spaces[0].string(0)}\n\n")

    print("lower bound", spaces[0].lower.x, spaces[0].lower.y, spaces[0].lower.z)
    print("upper bound", spaces[0].upper.x, spaces[0].upper.y, spaces[0].upper.z)

    for p in spaces[0].yield_all_points():
        print(f"active neighbours of {p}: {spaces[0].count_active_neighbours(p)}")
    # copied from day11: TODO change
    # i = 0
    # while True:
    #     src = spaces[i % 2]
    #     dst = spaces[(i + 1) % 2]
    #     array_changed = src.transform(dst)
    #     i += 1
    #     if not array_changed:
    #         print(f"array stopped changing after {i} iterations, with {src.count_all_occupied()} seats occupied")
    #         return


if __name__ == "__main__":
    main()
