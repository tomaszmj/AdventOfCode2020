from __future__ import annotations

import itertools
import math
from typing import List, Set, Iterable, Dict, Tuple
from dataclasses import dataclass


def safe_add_to_dict_of_sets(dictionary: Dict[object, Set[object]], key, value):
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


@dataclass
class TileTransformation:
    rotation: int = 0
    flip_up_down: int = 0
    flip_left_right: int = 0

    def __hash__(self):
        # hash as 4-bit integer: rotation (0-3): bits 0,1, flip_up_down: bit 2, flip_left_right: bit 3
        return self.rotation + (self.flip_up_down << 2) + (self.flip_left_right << 3)

    @classmethod
    def from_hash(cls, hash: int) -> TileTransformation:
        rotation = hash & 0b0011
        flip_up_down = (hash & 0b0100) >> 2
        flip_left_right = (hash & 0b1000) >> 3
        return TileTransformation(rotation, flip_up_down, flip_left_right)


class Tile:
    def __init__(self, text: List[str], number: int):
        self.number = number
        self.up = list(text[0])  # up in direction left->right - first line
        self.right = list((t[-1] for t in text))  # right in direction up->down - last character from each line
        self.down = list(text[-1])  # down in direction left->right - last line
        self.left = list((t[0] for t in text))  # left in direction up->down - first character from each line
        self.transformation = TileTransformation()

    # rotates tile clockwise once
    def rotate(self):
        self.up, self.right, self.down, self.left = self.left, self.up, self.right, self.down
        self.up.reverse()
        self.down.reverse()
        self.transformation.rotation = (self.transformation.rotation + 1) % 4

    def flip_up_down(self):
        self.up, self.down = self.down, self.up
        self.left.reverse()
        self.right.reverse()
        self.transformation.flip_up_down = (self.transformation.flip_up_down + 1) % 2

    def flip_left_right(self):
        self.left, self.right = self.right, self.left
        self.up.reverse()
        self.down.reverse()
        self.transformation.flip_left_right = (self.transformation.flip_left_right + 1) % 2

    def set_transformation(self, transformation: TileTransformation):
        while self.transformation.rotation != transformation.rotation:
            self.rotate()
        if self.transformation.flip_up_down != transformation.flip_up_down:
            self.flip_up_down()
        if self.transformation.flip_left_right != transformation.flip_left_right:
            self.flip_left_right()

    # warning, yield_all_transformations modifies Tile in place, so something like
    # list(tile.yield_all_transformations()) will not work
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


@dataclass
class TileSelection:
    number: int
    transformation: TileTransformation

    def __hash__(self):
        # transformation hash is 0-15, so by moving number 4 bits to the left,
        # we get a unique value for each (number, transformation) pair
        return self.transformation.__hash__() + (self.number << 4)

    def __str__(self):
        return f"{self.number},{self.transformation.__hash__()}"

    def __repr__(self):
        return f"{self.number},{self.transformation.__hash__()}"


class TileNeighbourhoodManager:
    def __init__(self, tiles: Iterable[Tile]):
        self.all_tile_numbers = list(t.number for t in tiles)
        print("precomputing neighbourhood")
        # print(f"precomputing neighbourhood by checking all pairs of (tile, transformation) -"
        #       f" {len(self.all_tile_numbers)*(len(self.all_tile_numbers)-1)*256} checks ...")
        # possible_neighbours maps tile number to set of possible neighbours, no matter how transformed
        self.possible_neighbours: Dict[int, Set[int]] = {}
        for t1, t2 in itertools.product(tiles, repeat=2):
            if t1.number == t2.number:
                continue
            self.save_neighbourhood_data(t1, t2)
        print("created TileNeighbourhoodManager")

    def save_neighbourhood_data(self, t1: Tile, t2: Tile):
        for tt1 in t1.yield_all_transformations():
            for tt2 in t2.yield_all_transformations():
                if tt1.right == tt2.left:  # tt2 in current state might be left to tt1
                    safe_add_to_dict_of_sets(self.possible_neighbours, tt1.number, tt2.number)
                    safe_add_to_dict_of_sets(self.possible_neighbours, tt2.number, tt1.number)
                    return
                if tt1.down == tt2.up:  # tt2 in current state might be under tt1
                    safe_add_to_dict_of_sets(self.possible_neighbours, tt1.number, tt2.number)
                    safe_add_to_dict_of_sets(self.possible_neighbours, tt2.number, tt1.number)
                    return

    def neighbours_len_stats(self) -> List[Tuple[int, int]]:
        neighbours_len = []
        for n, s in self.possible_neighbours.items():
            neighbours_len.append((n, len(s)))
        neighbours_len.sort(key=lambda nn: nn[1])
        return neighbours_len


def main():
    tiles: List[Tile] = []
    with open("data.txt") as f:
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
    neighbourhood_manager = TileNeighbourhoodManager(tiles)
    neighbours_len = neighbourhood_manager.neighbours_len_stats()
    print("tiles with smallest number of possible neighbours:")
    for i in range(min(len(neighbours_len), 5)):
        print(f"{neighbours_len[i][0]}: {neighbours_len[i][1]}")
    print("...\n")
    # Checked experimentally that there are only 4 tiles with 2 possible neighbours ... so they must be corners!
    # BTW, I do not like such puzzles that have solution depending on specific dataset properties.
    print(f"solution: {math.prod(n[0] for n in neighbours_len[:4])}")


if __name__ == "__main__":
    main()
