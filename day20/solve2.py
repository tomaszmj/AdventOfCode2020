from __future__ import annotations

import itertools
import math
import copy
from typing import List, Set, Iterable, Dict, NamedTuple, Tuple
from dataclasses import dataclass


HALF_TILE_LEN = 5


class Matrix2x2:
    # all_transformations will be filled in by precompute_transformations.
    # This is list of all possible tile transformations in this puzzle:
    # combined rotations and flipping in 2 axes.
    _all_transformations: List[Matrix2x2] = []

    def __init__(self, a: int, b: int, c: int, d: int):
        self.a: int = a
        self.b: int = b
        self.c: int = c
        self.d: int = d

    @classmethod
    def all_transformations(cls) -> List[Matrix2x2]:
        if len(cls._all_transformations) == 0:
            cls._precompute_transformations()
        return cls._all_transformations

    @classmethod
    def _precompute_transformations(cls):
        rotate = Matrix2x2(0, 1, -1, 0)
        flip_horizontal_axis = Matrix2x2(1, 0, 0, -1)
        flip_vertical_axis = Matrix2x2(-1, 0, 0, 1)
        flip_both_axes = flip_horizontal_axis.multiply_left(flip_vertical_axis)
        m = Matrix2x2(1, 0, 0, 1)  # start with identity
        for _ in range(4):  # for each rotation
            # for each transformation we save inverted matrices, so that we can compute
            # original coordinates given transformed coordinates (transformations
            # will be used to read transformed tile data without modifying tile)
            cls.add_to_all_transformations(m.copy())  # without flipping
            cls.add_to_all_transformations(m.multiply_left(flip_horizontal_axis).inverse())
            cls.add_to_all_transformations(m.multiply_left(flip_vertical_axis).inverse())
            cls.add_to_all_transformations(m.multiply_left(flip_both_axes).inverse())
            m = m.multiply_left(rotate)  # go to next rotation
    
    @classmethod
    def add_to_all_transformations(cls, m: Matrix2x2):
        for t in cls._all_transformations:
            if t == m:
                return
        cls._all_transformations.append(m)

    # multiply_left returns m * self
    def multiply_left(self, m: Matrix2x2) -> Matrix2x2:
        return Matrix2x2(
            m.a * self.a + m.b * self.c, m.a * self.b + m.b * self.d,
            m.c * self.a + m.d * self.c, m.c * self.b + m.d * self.d,
        )

    def copy(self) -> Matrix2x2:
        return Matrix2x2(
            self.a, self.b,
            self.c, self.d,
        )

    def inverse(self) -> Matrix2x2:
        det = self.a * self.d - self.b * self.c
        if det != 1 and det != -1:
            # Matrices used in precompute_transformations: identity, rotations, flipping
            # always have determinant 1. Thanks to that, inverted matrices still have
            # coordinates of type int - we do not use floating point arithmetic here.
            # This code does not have to be generic, so just raise excpetion if we have other determinant.
            raise RuntimeError("all matrices we use here should have determinant 1 or -1")
        # Normally results should be divided by det, but thanks to property described above 1/det = det
        return Matrix2x2(
            self.d * det, -self.b * det,
            -self.c * det, self.a * det,
        )

    # multiply_by_vector_right returns self * vertical_vector[x, y]
    def multiply_by_vector_right(self, x: int, y: int) -> Tuple[int, int]:
        return self.a * x + self.b * y, self.c * x + self.d * y

    def __str__(self):
        return f"[{self.a} {self.b} | {self.c} {self.d}]"

    def __eq__(self, other):
        if not isinstance(other, Matrix2x2):
            return False
        return self.a == other.a and \
            self.b == other.b and \
            self.c == other.c and \
            self.d == other.d



def safe_add_to_dict_of_sets(dictionary: Dict[object, Set[object]], key, value):
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


class Tile:
    # Tile data coordiante systsem is constructed in a way that allows
    # to transform tile by just changing transformation matrix.
    # Transformation matrices represent linear transformations in 2D space.
    # For it to work, tile data coordinates must be centred at (0, 0) and symmetric
    # These are discrete coordinates and tile size (10x10) is even, so y=0 and x=0 must
    # be skipped for symetry. On example picture below coordinates a = (-5, -5) and b = (5, 5).
    # a    |
    #      |
    #      |
    #      |
    #      |
    # -----#-----> X
    #      |
    #      |
    #      |
    #      |
    #      |    b
    #      Y
    def __init__(self, text: List[str], number: int):
        self.number = number
        self.data: Dict[Tuple[int, int], str] = {}
        x, y = -HALF_TILE_LEN, -HALF_TILE_LEN
        for line in text:
            x = -HALF_TILE_LEN
            for c in line:
                self.data[(x, y)] = c
                x += 1
                if x == 0:  # skip x = 0 for symmetry described above
                    x += 1
            y += 1
            if y == 0:  # skip y = 0 for symmetry described above
                y += 1

    # get reads given position from Tile data.
    # x, y are cooridinates in current transformation,
    # for example if tile has been flipped around X axis,
    # tile's up border will still be y = -5, x in [-5:-1, 1:5], i.e. the caller
    # should use the same coordinates for given tile element regardless of transformation.
    # transformation passed as 3-rd argument is inversed matrix of tile transformation,
    # such matrices are already there in Matrix2x2.all_transformations
    def get(self, x: int, y: int, transformation: Matrix2x2) -> str:
        original_x, original_y = transformation.multiply_by_vector_right(x, y)
        return self.data[(original_x, original_y)]

    def up(self, transformation: Matrix2x2) -> str:
        all_x = itertools.chain(range(-5, 0), range(1, 6))
        y = -5
        return "".join(self.get(x, y, transformation) for x in all_x)

    def right(self, transformation: Matrix2x2) -> str:
        x = 5
        all_y = itertools.chain(range(-5, 0), range(1, 6))
        return "".join(self.get(x, y, transformation) for y in all_y)

    def down(self, transformation: Matrix2x2) -> str:
        all_x = itertools.chain(range(-5, 0), range(1, 6))
        y = 5
        return "".join(self.get(x, y, transformation) for x in all_x)

    def left(self, transformation: Matrix2x2) -> str:
        x = -5
        all_y = itertools.chain(range(-5, 0), range(1, 6))
        return "".join(self.get(x, y, transformation) for y in all_y)


class TileSelection(NamedTuple):
    number: int
    transformation_index: int


class TileWithDegree(NamedTuple):
    number: int
    degree: int


class TileNeighbourhoodManager:
    def __init__(self, tiles: Iterable[Tile]):
        self.all_tile_numbers = list(t.number for t in tiles)
        self.tiles_with_degrees: List[TileWithDegree] = []
        # *_successors map tile number to set of possible tile numbers next to given tile
        self.right_successors: Dict[TileSelection, Set[TileSelection]] = {}
        self.down_successors: Dict[TileSelection, Set[TileSelection]] = {}
        print(f"precomputing neighbourhood by checking all pairs of (tile, transformation) -"
              f" {len(self.all_tile_numbers)*(len(self.all_tile_numbers)-1)*256} checks ...")
        self.prepare_neighbourhood_data(tiles)
        print(f"created TileNeighbourhoodManager with {len(self.right_successors)} right "
              f"successors and {len(self.down_successors)} down successors")

    def prepare_neighbourhood_data(self, tiles: Iterable[Tile]):
        possible_neighbours: Dict[int, Set[int]] = {}
        for t1, t2 in itertools.product(tiles, repeat=2):
            if t1.number == t2.number:
                continue
            for tr1_index, tr1 in enumerate(Matrix2x2.all_transformations()):
                for tr2_index, tr2 in enumerate(Matrix2x2.all_transformations()):
                    if t1.right(tr1) == t2.left(tr2):  # t2 in current transformation might be left to t1
                        selection1 = TileSelection(t1.number, tr1_index)
                        selection2 = TileSelection(t2.number, tr2_index)
                        safe_add_to_dict_of_sets(self.right_successors, selection1, selection2)
                        safe_add_to_dict_of_sets(possible_neighbours, t1.number, t2.number)
                        safe_add_to_dict_of_sets(possible_neighbours, t2.number, t1.number)
                    if t1.down(tr1) == t2.up(tr2):  # t2 in current transformation might be under t1
                        selection1 = TileSelection(t1.number, tr1_index)
                        selection2 = TileSelection(t2.number, tr2_index)
                        safe_add_to_dict_of_sets(self.down_successors, selection1, selection2)
                        safe_add_to_dict_of_sets(possible_neighbours, t1.number, t2.number)
                        safe_add_to_dict_of_sets(possible_neighbours, t2.number, t1.number)
        for n, s in possible_neighbours.items():
            self.tiles_with_degrees.append(TileWithDegree(number=n, degree=len(s)))
        self.tiles_with_degrees.sort(key=lambda t: t.degree)

    def stats(self):
        print("tiles with number of possible neighbours:")
        for td in self.tiles_with_degrees:
            print(f"{td.number}: {td.degree}")

    # def possible_new_tiles(self, left_neighbour: Tile, up_neighbour: Tile, chosen_numbers_set: Set[int]) -> Iterable[TileSelection]:
    #     if left_neighbour and up_neighbour:
    #         left_candidates = self.right_successors_per_tile(left_neighbour)
    #         up_candidates = self.down_successors_per_tile(up_neighbour)
    #         for selection in left_candidates.intersection(up_candidates):
    #             if selection.number not in chosen_numbers_set:
    #                 yield selection
    #     elif left_neighbour:
    #         for selection in self.right_successors_per_tile(left_neighbour):
    #             if selection.number not in chosen_numbers_set:
    #                 yield selection
    #     elif up_neighbour:
    #         for selection in self.down_successors_per_tile(up_neighbour):
    #             if selection.number not in chosen_numbers_set:
    #                 yield selection
    #     else:  # no neighbours - yield all possible transformations of all tiles
    #         for tile_number, transformation_hash in itertools.product(
    #                 filter(lambda n: n not in chosen_numbers_set, self.all_tile_numbers), range(16)):
    #             yield TileSelection(tile_number, TileTransformation.from_hash(transformation_hash))

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

    def coordinates(self, list_index: int) -> Tuple[int, int]:
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
        neighbourhood_manager = TileNeighbourhoodManager(self.all_tiles.values())
        chosen_tiles: List[Tile] = []
        print(f"solving by backtracking for {len(self.all_tiles)} tiles ...")
        if self._solve(chosen_tiles, set(), neighbourhood_manager):
            return chosen_tiles
        return []

    def _solve(self, chosen_tiles: List[Tile], chosen_numbers_set: Set[int],
               neighbourhood_manager: TileNeighbourhoodManager) -> bool:
        if len(chosen_tiles) == len(self.all_tiles):
            return True
        new_x, new_y = self.indexer.coordinates(len(chosen_tiles))
        left_neighbour = chosen_tiles[self.indexer.list_index(new_x - 1, new_y)] if new_x > 0 else None
        up_neighbour = chosen_tiles[self.indexer.list_index(new_x, new_y - 1)] if new_y > 0 else None
        for selection in neighbourhood_manager.possible_new_tiles(left_neighbour, up_neighbour, chosen_numbers_set):
            # print(f"solving ({self.chosen_tiles_to_string(chosen_tiles)}) - "
            #       f"selection {selection.number},{selection.transformation.__hash__()}")
            # select tile - neighbourhood_manager already guarantees that it will match
            tile = self.all_tiles[selection.number]
            old_transformation = copy.deepcopy(tile.transformation)
            chosen_numbers_set.add(tile.number)
            tile.set_transformation(selection.transformation)
            chosen_tiles.append(tile)
            if self._solve(chosen_tiles, chosen_numbers_set, neighbourhood_manager):
                return True
            # recursive _solve failed - backtrack ...
            chosen_tiles.pop()
            tile.set_transformation(old_transformation)
            chosen_numbers_set.remove(tile.number)
        return False

    # returns multiplied IDs of the four corner tiles, required as puzzle answer
    def magic_number(self, chosen_tiles: List[Tile]) -> int:
        return math.prod((chosen_tiles[i].number for i in self.indexer.indices_of_matrix_corners()))

    @staticmethod
    def chosen_tiles_to_string(chosen_tiles: List[Tile]) -> str:
        return " ".join(f"{c.number},{c.transformation.__hash__()}" for c in chosen_tiles)


def main():
    tiles: List[Tile] = []
    with open("data.txt") as f:
        line = f.readline().strip()
        while line:
            if line[:4] != "Tile":
                raise ValueError(f"expected Tile header, got {line}")
            number = int(line[5:9])
            data = []
            for i in range(2 * HALF_TILE_LEN):
                line = f.readline().strip()
                data.append(line)
            tiles.append(Tile(data, number))
            line = f.readline().strip()
            if line:
                raise ValueError(f"expected empty line, got {line}")
            line = f.readline().strip()
    neighbourhood_manager = TileNeighbourhoodManager(tiles)
    neighbourhood_manager.stats()
    # image = Image(tiles)
    # chosen_tiles = image.solve()
    # if chosen_tiles:
    #     print(f"solution {image.magic_number(chosen_tiles)}")
    # else:
    #     print("could not find solution :(")


if __name__ == "__main__":
    main()
