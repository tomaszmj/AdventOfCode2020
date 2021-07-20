from __future__ import annotations

import itertools
import math
import copy
from typing import List, Set, Iterable, Dict
from dataclasses import dataclass


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
        # map tile number to set of possible tile numbers next to given tile
        self.right_successors: Dict[TileSelection, Set[TileSelection]] = {}
        self.down_successors: Dict[TileSelection, Set[TileSelection]] = {}
        self.all_tile_numbers = list(t.number for t in tiles)
        for t1, t2 in itertools.product(tiles, repeat=2):
            if t1.number == t2.number:
                continue
            for tt1 in t1.yield_all_transformations():
                for tt2 in t2.yield_all_transformations():
                    if tt1.right == tt2.left:  # tt2 in current state might be left to tt1
                        tt1_state = TileSelection(tt1.number, copy.deepcopy(tt1.transformation))
                        tt2_state = TileSelection(tt2.number, copy.deepcopy(tt2.transformation))
                        if tt1_state not in self.right_successors:
                            self.right_successors[tt1_state] = set()
                        self.right_successors[tt1_state].add(tt2_state)
                    if tt1.down == tt2.up:  # tt2 in current state might be under tt1
                        tt1_state = TileSelection(tt1.number, copy.deepcopy(tt1.transformation))
                        tt2_state = TileSelection(tt2.number, copy.deepcopy(tt2.transformation))
                        if tt1_state not in self.down_successors:
                            self.down_successors[tt1_state] = set()
                        self.down_successors[tt1_state].add(tt2_state)

    def possible_new_tiles(self, left_neighbour: Tile, up_neighbour: Tile) -> Iterable[TileSelection]:
        if left_neighbour and up_neighbour:
            left_candidates = self.right_successors_per_tile(left_neighbour)
            up_candidates = self.down_successors_per_tile(up_neighbour)
            for selection in left_candidates.intersection(up_candidates):
                yield selection
        elif left_neighbour:
            for selection in self.right_successors_per_tile(left_neighbour):
                yield selection
        elif up_neighbour:
            for selection in self.down_successors_per_tile(up_neighbour):
                yield selection
        else:  # no neighbours - yield all possible transformations of all tiles
            for n, transformation_hash in itertools.product(self.all_tile_numbers, range(16)):
                yield TileSelection(n, TileTransformation.from_hash(transformation_hash))

    def right_successors_per_tile(self, tile: Tile) -> Set[TileSelection]:
        key = TileSelection(tile.number, tile.transformation)
        if key not in self.right_successors:
            return set()
        return self.right_successors[key]

    def down_successors_per_tile(self, tile: Tile) -> Set[TileSelection]:
        key = TileSelection(tile.number, tile.transformation)
        if key not in self.down_successors:
            return set()
        return self.down_successors[key]


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
        self.all_tiles: Dict[int, Tile] = {}
        for t in tiles:
            self.all_tiles[t.number] = t
        size = int(math.sqrt(len(tiles)))
        if size ** 2 != len(tiles):
            raise ValueError(f"number of tiles {len(tiles)} is not a square of natural number")
        self.indexer = ListToMatrixIndexer(size, size)

    # solve will try to put all tiles to their places so that they match.
    # It returns list of chosen tiles on success, empty list on failure
    def solve(self) -> List[Tile]:
        print(f"precomputing neighbourhood by checking all pairs of (tile, transformation) -"
              f" {len(self.all_tiles)*(len(self.all_tiles)-1)*256} checks ...")
        neighbourhood_manager = TileNeighbourhoodManager(self.all_tiles.values())
        chosen_tiles: List[Tile] = []
        # print("neighbourhood_manager possible new tiles test:")
        # print(f"no constraints: {len(list(neighbourhood_manager.possible_new_tiles(None, None)))}")
        # tile = self.all_tiles[1951]
        # for trans in range(16):
        #     tile.set_transformation(TileTransformation.from_hash(trans))
        #     print(f"for tile {tile.number},{tile.transformation.__hash__()}: "
        #           f"{list(neighbourhood_manager.possible_new_tiles(tile, None))}\n")
        # print("all right successors:")
        # for key, value in neighbourhood_manager.right_successors.items():
        #     print(f"{key}: {list(value)}")
        # print("all down successors:")
        # for key, value in neighbourhood_manager.down_successors.items():
        #     print(f"{key}: {list(value)}")
        # return []
        print(f"solving by backtracking for {len(self.all_tiles)} tiles ...")
        if self._solve(chosen_tiles, set(), neighbourhood_manager):
            return chosen_tiles
        return []

    def _solve(self, chosen_tiles: List[Tile], chosen_numbers_set: Set[int],
               neighbourhood_manager: TileNeighbourhoodManager) -> bool:
        if len(chosen_tiles) == len(self.all_tiles):
            return True
        # We iterate over all possible tiles numbers, filtered by chosen_numbers_set instead of just
        # using available numbers set, because we cannot add/remove items to the set while iterating over it
        new_x, new_y = self.indexer.coordinates(len(chosen_tiles))
        left_neighbour = chosen_tiles[self.indexer.list_index(new_x - 1, new_y)] if new_x > 0 else None
        up_neighbour = chosen_tiles[self.indexer.list_index(new_x, new_y - 1)] if new_y > 0 else None
        for selection in neighbourhood_manager.possible_new_tiles(left_neighbour, up_neighbour):
            if selection.number in chosen_numbers_set:
                continue
            chosen_numbers_set.add(selection.number)
            tile = copy.deepcopy(self.all_tiles[selection.number])
            tile.set_transformation(selection.transformation)
            print(f"solving ({self.chosen_tiles_to_string(chosen_tiles)}) - "
                  f"selection {tile.number},{selection.transformation.__hash__()}")
            if not self.new_tile_matches(chosen_tiles, tile):
                raise RuntimeError(f"something went wrong adding {selection.number},{selection.transformation} to "
                                   f"chosen [{self.chosen_tiles_to_string(chosen_tiles)}]")
            chosen_tiles.append(tile)
            if self._solve(chosen_tiles, chosen_numbers_set, neighbourhood_manager):
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
        return " ".join(f"{c.number},{c.transformation.__hash__()}" for c in chosen_tiles)


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
