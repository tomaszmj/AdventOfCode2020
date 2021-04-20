from __future__ import annotations

import functools
import itertools
import operator
from typing import NamedTuple, Set, Iterable


ACTIVE = "#"
INACTIVE = "."


class Point(NamedTuple):
    x: int
    y: int
    z: int


# Space represents ACTIVE/INACTIVE points in infinite discrete Euclidean space:
#   y
#   ^
#   |
#   --> x
#  /
# z
# Initially all points are INACTIVE, so we store only the ACTIVE ones in a set,
# together with upper/lower bounds, i.e. lowest/highest coordinates for which
# point was seen active (thanks to it we can iterate for each Conway box).
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
            # We do not modify lower/upper bounds here, as it is not necessary and would
            # require time-consuming search of new bounds or proper data structure for such search.
            # Bounds can be larger than they should, as they are only to simplify iteration (space is infinite).
            self.actives.remove(p)

    def yield_all_points(self) -> Iterable[Point]:
        for p in itertools.product(
            range(self.lower.x, self.upper.x + 1, 1),
            range(self.lower.y, self.upper.y + 1, 1),
            range(self.lower.z, self.upper.z + 1, 1)
        ):
            yield Point(p[0], p[1], p[2])

    def yield_all_points_with_outliers(self) -> Iterable[Point]:
        for p in itertools.product(
                range(self.lower.x - 1, self.upper.x + 2, 1),
                range(self.lower.y - 1, self.upper.y + 2, 1),
                range(self.lower.z - 1, self.upper.z + 2, 1)
        ):
            yield Point(p[0], p[1], p[2])

    @staticmethod
    def yield_point_neighbours(p: Point) -> Iterable[Point]:
        for diff in itertools.product((-1, 0, 1), repeat=3):
            if diff != (0, 0, 0):
                yield Point(p.x + diff[0], p.y + diff[1], p.z + diff[2])

    def string(self, z: int) -> str:
        return "\n".join(
            "".join(self.get(Point(x, y, z)) for x in range(self.lower.x, self.upper.x + 1, 1))
            for y in range(self.upper.y, self.lower.y - 1, -1)
        )

    def count_active_neighbours(self, p: Point) -> int:
        return functools.reduce(operator.add, (1 if self.get(n) == ACTIVE else 0 for n in self.yield_point_neighbours(p)))

    def transform_to(self, dst: Space):
        for p in self.yield_all_points_with_outliers():
            active_neighbours = self.count_active_neighbours(p)
            if self.get(p) == ACTIVE:
                if active_neighbours == 2 or active_neighbours == 3:
                    dst.set_active(p)
                else:
                    dst.set_inactive(p)
            else:
                if active_neighbours == 3:
                    dst.set_active(p)
                else:
                    dst.set_inactive(p)

    def count_actives(self) -> int:
        return len(self.actives)


def main():
    spaces = [Space(), Space()]
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                spaces[0].add_row(line)
    iterations = 6
    for i in range(iterations):
        src = spaces[i % 2]
        dst = spaces[(i + 1) % 2]
        src.transform_to(dst)
    print(f"after {iterations} iterations: {spaces[iterations % 2].count_actives()}")


if __name__ == "__main__":
    main()
