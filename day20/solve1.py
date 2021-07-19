from __future__ import annotations

import math
from typing import List, Set, Iterable


class Tile:
    def __init__(self, text: List[str], number: int):
        self.number = number
        self.up = list(text[0])  # up in direction left->right - first line
        self.right = list((t[-1] for t in text))  # right in direction up->down - last character from each line
        self.down = list(text[-1])  # down in direction left->right - last line
        self.left = list((t[0] for t in text))  # left in direction up->down - first character from each line

    # rotates tile clockwise once
    def rotate(self):
        self.up, self.right, self.down, self.left = self.left, self.up, self.right, self.down
        self.up.reverse()
        self.down.reverse()

    def flip_up_down(self):
        self.up, self.down = self.down, self.up
        self.left.reverse()
        self.right.reverse()

    def flip_left_right(self):
        self.left, self.right = self.right, self.left
        self.up.reverse()
        self.down.reverse()

    def yield_all_transformations(self) -> Iterable[Tile]:
        for rotation in range(4):  # for each rotation
            yield self  # without flipping
            self.flip_left_right()
            yield self  # with flip_left_right
            self.flip_left_right()  # reverts flip_left_right
            self.flip_up_down()
            yield self  # with flip_up_down
            self.flip_left_right()
            yield self  # with flip_up_down and flip_left_right
            self.flip_left_right()  # reverts flip_left_right
            self.flip_up_down()  # reverts flip_up_down
            self.rotate()  # go to next rotation - or (in case of last iteration) reset to original rotation


class ListToMatrixIndexer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def list_index(self, x: int, y: int) -> int:
        return y * self.width + x

    def coordinates(self, list_index: int) -> (int, int):
        y = list_index // self.width
        x = list_index % self.width
        return x, y

    def indices_of_matrix_corners(self) -> List[int]:
        return [
            0,
            self.list_index(self.width - 1, 0),
            self.list_index(0, self.height - 1),
            self.list_index(self.width - 1, self.height - 1),
        ]


class Image:
    def __init__(self, tiles: List[Tile]):
        self.all_tiles = tiles
        size = int(math.sqrt(len(tiles)))
        if size ** 2 != len(tiles):
            raise ValueError(f"number of tiles {len(tiles)} is not a square of natural number")
        self.indexer = ListToMatrixIndexer(size, size)

    # solve will try to put all tiles to their places so that they match.
    # It returns list of chosen tiles on success, empty list on failure
    def solve(self) -> List[Tile]:
        chosen_tiles: List[Tile] = []
        if self._solve(chosen_tiles, set()):
            return chosen_tiles
        return []

    def _solve(self, chosen_tiles: List[Tile], chosen_numbers_set: Set[int]) -> bool:
        # print(f"_solve({self.chosen_tiles_to_string(chosen_tiles)}) ...")
        if len(chosen_tiles) == len(self.all_tiles):
            return True
        # We iterate over all possible tiles numbers, filtered by chosen_numbers_set instead of just
        # using available numbers set, because we cannot add/remove items to the set while iterating over it
        for tile in self.all_tiles:
            if tile.number in chosen_numbers_set:
                continue
            chosen_numbers_set.add(tile.number)
            for tt in tile.yield_all_transformations():
                if self.new_tile_matches(chosen_tiles, tt):
                    chosen_tiles.append(tt)
                    if self._solve(chosen_tiles, chosen_numbers_set):
                        return True
                    chosen_tiles.pop()
            chosen_numbers_set.remove(tile.number)
        return False

    def new_tile_matches(self, chosen_tiles: List[Tile], new_tile: Tile) -> bool:
        new_x, new_y = self.indexer.coordinates(len(chosen_tiles))
        if new_x > 0:
            left_neighbour_index = self.indexer.list_index(new_x - 1, new_y)
            left_neighbour = chosen_tiles[left_neighbour_index]
            if left_neighbour.right != new_tile.left:
                return False
        if new_y > 0:
            up_neighbour_index = self.indexer.list_index(new_x, new_y - 1)
            up_neighbour = chosen_tiles[up_neighbour_index]
            if up_neighbour.down != new_tile.up:
                return False
        # we are putting new tiles left-to-right, up-down, so new tile will never have neighbours right or down
        return True

    # returns multiplied IDs of the four corner tiles, required as puzzle answer
    def magic_number(self, chosen_tiles: List[Tile]) -> int:
        return math.prod((chosen_tiles[i].number for i in self.indexer.indices_of_matrix_corners()))

    @staticmethod
    def chosen_tiles_to_string(chosen_tiles: List[Tile]) -> str:
        return " ".join(f"{c.number}" for c in chosen_tiles)


def main():
    tiles: List[Tile] = []
    with open("data_small.txt") as f:
        line = f.readline().strip()
        while line:
            if line[:4] != "Tile":
                raise ValueError(f"expected Tile header, got {line}")
            number = int(line[5:9])
            data = []
            for i in range(10):
                line = f.readline().strip()
                data.append(line)
            tiles.append(Tile(data, number))
            line = f.readline().strip()
            if line:
                raise ValueError(f"expected empty line, got {line}")
            line = f.readline().strip()
    print(f"solving for {len(tiles)} tiles...")
    image = Image(tiles)
    chosen_tiles = image.solve()
    if chosen_tiles:
        print(f"solution {image.magic_number(chosen_tiles)}")
    else:
        print("could not find solution :(")


if __name__ == "__main__":
    main()
