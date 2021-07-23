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
    all_transformations: List[Matrix2x2] = []

    def __init__(self, a: int, b: int, c: int, d: int):
        self.a: int = a
        self.b: int = b
        self.c: int = c
        self.d: int = d

    @classmethod
    def precompute_transformations(cls):
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
        for t in cls.all_transformations:
            if t == m:
                return
        cls.all_transformations.append(m)


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
        if isinstance(other, Matrix2x2):
            return self.a == other.a and \
                self.b == other.b and \
                self.c == other.c and \
                self.d == other.d
        return False



def safe_add_to_dict_of_sets(dictionary: Dict[object, Set[object]], key, value):
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


class Tile2:
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
                if x == 0:  # skip x = 0
                    x += 1
            y += 1
            if y == 0:
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
            for tt1 in t1.yield_all_transformations():
                for tt2 in t2.yield_all_transformations():
                    if tt1.right == tt2.left:  # tt2 in current state might be left to tt1
                        tt1_state = TileSelection(tt1.number, copy.deepcopy(tt1.transformation))
                        tt2_state = TileSelection(tt2.number, copy.deepcopy(tt2.transformation))
                        safe_add_to_dict_of_sets(self.right_successors, tt1_state, tt2_state)
                        safe_add_to_dict_of_sets(possible_neighbours, tt1.number, tt2.number)
                        safe_add_to_dict_of_sets(possible_neighbours, tt2.number, tt1.number)
                    if tt1.down == tt2.up:  # tt2 in current state might be under tt1
                        tt1_state = TileSelection(tt1.number, copy.deepcopy(tt1.transformation))
                        tt2_state = TileSelection(tt2.number, copy.deepcopy(tt2.transformation))
                        safe_add_to_dict_of_sets(self.down_successors, tt1_state, tt2_state)
                        safe_add_to_dict_of_sets(possible_neighbours, tt1.number, tt2.number)
                        safe_add_to_dict_of_sets(possible_neighbours, tt2.number, tt1.number)
        for n, s in possible_neighbours.items():
            self.tiles_with_degrees.append(TileWithDegree(number=n, degree=len(s)))
        self.tiles_with_degrees.sort(key=lambda t: t.degree)

    def stats(self):
        print("tiles with number of possible neighbours:")
        for td in self.tiles_with_degrees:
            print(f"{td.number}: {td.degree}")

    def possible_new_tiles(self, left_neighbour: Tile, up_neighbour: Tile, chosen_numbers_set: Set[int]) -> Iterable[TileSelection]:
        if left_neighbour and up_neighbour:
            left_candidates = self.right_successors_per_tile(left_neighbour)
            up_candidates = self.down_successors_per_tile(up_neighbour)
            for selection in left_candidates.intersection(up_candidates):
                if selection.number not in chosen_numbers_set:
                    yield selection
        elif left_neighbour:
            for selection in self.right_successors_per_tile(left_neighbour):
                if selection.number not in chosen_numbers_set:
                    yield selection
        elif up_neighbour:
            for selection in self.down_successors_per_tile(up_neighbour):
                if selection.number not in chosen_numbers_set:
                    yield selection
        else:  # no neighbours - yield all possible transformations of all tiles
            for tile_number, transformation_hash in itertools.product(
                    filter(lambda n: n not in chosen_numbers_set, self.all_tile_numbers), range(16)):
                yield TileSelection(tile_number, TileTransformation.from_hash(transformation_hash))

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
    tiles2: List[Tile2] = []
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
            tiles2.append(Tile2(data, number))
            line = f.readline().strip()
            if line:
                raise ValueError(f"expected empty line, got {line}")
            line = f.readline().strip()

    result_old_up = set()
    tile = tiles[0]
    for tt in tile.yield_all_transformations():
        result_old_up.add("".join(tt.up))
    print(sorted(list(result_old_up)))

    Matrix2x2.precompute_transformations()
    tile2 = tiles2[0]
    result_new_up = set()
    for t in Matrix2x2.all_transformations:
        result_new_up.add(tile2.up(t))
    print(sorted(list(result_new_up)))

    for tt in Matrix2x2.all_transformations:
        print(tt)
    # neighbourhood_manager = TileNeighbourhoodManager(tiles)
    # neighbourhood_manager.stats()
    # image = Image(tiles)
    # chosen_tiles = image.solve()
    # if chosen_tiles:
    #     print(f"solution {image.magic_number(chosen_tiles)}")
    # else:
    #     print("could not find solution :(")


if __name__ == "__main__":
    main()
