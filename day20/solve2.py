from __future__ import annotations

import itertools
import math
import time
from typing import List, Set, Iterable, Dict, NamedTuple, Tuple, Callable


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
        size = len(text)
        if size == 0 or any((size != len(t) for t in text)):
            raise ValueError(f"invalid text passed in Tile constructor, expected square size, got:\n{text}")
        # coordinates could be implemented for odd size as well, but it would complicate
        # implementation and it is not needed for the data we have, so only even size is accepted
        if size % 2 == 1:
            raise ValueError(f"Tile supports only even size, got {size}")
        self.half_size = size // 2
        x, y = -self.half_size, -self.half_size
        for line in text:
            x = -self.half_size
            for c in line:
                self.data[(x, y)] = c
                x += 1
                if x == 0:  # skip x = 0 for symmetry described above
                    x += 1
            y += 1
            if y == 0:  # skip y = 0 for symmetry described above
                y += 1

    # get reads given position from Tile data.
    # x, y are coordinates in current transformation,
    # for example if tile has been flipped around X axis,
    # tile's up border will still be y = -5, x in [-5:-1, 1:5], i.e. the caller
    # should use the same coordinates for given tile element regardless of transformation.
    # transformation passed as 3-rd argument is inversed matrix of tile transformation,
    # such matrices are already there in Matrix2x2.all_transformations
    def get(self, x: int, y: int, transformation: Matrix2x2) -> str:
        original_x, original_y = transformation.multiply_by_vector_right(x, y)
        return self.data[(original_x, original_y)]

    def up(self, transformation: Matrix2x2) -> str:
        all_x = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        y = -self.half_size
        return "".join(self.get(x, y, transformation) for x in all_x)

    def right(self, transformation: Matrix2x2) -> str:
        x = self.half_size
        all_y = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        return "".join(self.get(x, y, transformation) for y in all_y)

    def down(self, transformation: Matrix2x2) -> str:
        all_x = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        y = self.half_size
        return "".join(self.get(x, y, transformation) for x in all_x)

    def left(self, transformation: Matrix2x2) -> str:
        x = -self.half_size
        all_y = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        return "".join(self.get(x, y, transformation) for y in all_y)

    def row(self, y: int, transformation: Matrix2x2) -> str:
        if y < -self.half_size or y == 0 or y > self.half_size:
            raise ValueError(f"invalid y for row: {y}")
        all_x = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        return "".join(self.get(x, y, transformation) for x in all_x)

    def interior_row(self, y: int, transformation: Matrix2x2) -> str:
        if y <= -self.half_size or y == 0 or y >= self.half_size:
            raise ValueError(f"invalid y for interior_row: {y}")
        # all_x is smaller range than above, because only interior elements are used
        all_x = itertools.chain(range(-self.half_size + 1, 0), range(1, self.half_size))
        return "".join(self.get(x, y, transformation) for x in all_x)

    def all_data_as_list(self, transformation: Matrix2x2) -> List[str]:
        # This function is poor in terms of performance, because it performs brutal matrix
        # multiplication for each coordinate pair just to read all data from dict in proper order.
        # But it turned out that this performance is more than enough, because our image is small.
        all_y = itertools.chain(range(-self.half_size, 0), range(1, self.half_size + 1))
        return list((self.row(y, transformation) for y in all_y))


class TileSelection(NamedTuple):
    number: int
    transformation_index: int


class TileWithDegree(NamedTuple):
    number: int
    degree: int


class TileNeighbour(NamedTuple):
    neighbour: TileSelection
    direction_from_neighbour: str
    # direction_from_neighbour is right / up / left / down, direction FROM NEIGHBOUR to some selected base position
    # for example for tiles AB, B being base position, tile A is neighbour with direction right


class TileNeighbourhoodManager:
    def __init__(self, all_tiles: Dict[int, Tile]):
        t1 = time.time()
        print(f"creating TileNeighbourhoodManager ...")
        self.all_tiles = all_tiles
        self.tiles_with_degrees: List[TileWithDegree] = []
        # *_successors map tile number to set of possible tile numbers next to given tile
        self.right_successors: Dict[TileSelection, Set[TileSelection]] = {}
        self.down_successors: Dict[TileSelection, Set[TileSelection]] = {}
        # we could also add left / up successors, but currently image is filled in left-to-right, up-down,
        # so newly added tile will never have neighbours above / to the left
        self.prepare_neighbourhood_data()
        t2 = time.time()
        print(f"created TileNeighbourhoodManager in {t2-t1}s with {len(self.right_successors)} right "
              f"successors and {len(self.down_successors)} down successors")

    def prepare_neighbourhood_data(self):
        possible_neighbours = self.check_possible_neighbours()
        self.fill_in_successors(possible_neighbours)
        for n, s in possible_neighbours.items():
            self.tiles_with_degrees.append(TileWithDegree(number=n, degree=len(s)))
        self.tiles_with_degrees.sort(key=lambda t: t.degree)

    # check_possible_neighbours returns dict mapping tile number to
    # the set of its possible neighbours, no matter how transformed
    def check_possible_neighbours(self) -> Dict[int, Set[int]]:
        time1 = time.time()
        possible_neighbours: Dict[int, Set[int]] = {}
        neutral_transform = Matrix2x2.all_transformations()[0]
        for t1, t2 in itertools.product(self.all_tiles.values(), repeat=2):
            if t1.number == t2.number:
                continue
            right1 = t1.right(neutral_transform)
            down1 = t1.down(neutral_transform)
            left1 = t1.left(neutral_transform)
            up1 = t1.up(neutral_transform)
            for tr2 in Matrix2x2.all_transformations():
                if right1 == t2.left(tr2) or down1 == t2.up(tr2) or left1 == t2.right(tr2) or up1 == t2.down(tr2):
                    self.safe_add_to_dict_of_sets(possible_neighbours, t1.number, t2.number)
                    self.safe_add_to_dict_of_sets(possible_neighbours, t2.number, t1.number)
                    break
        time2 = time.time()
        print(f"check_possible_neighbours done in {time2-time1}s")
        return possible_neighbours

    def fill_in_successors(self, possible_neighbours: Dict[int, Set[int]]):
        for tile1_number, neighbours in possible_neighbours.items():
            tile1 = self.all_tiles[tile1_number]
            for tr1_index, tr1 in enumerate(Matrix2x2.all_transformations()):
                selection1 = TileSelection(tile1_number, tr1_index)
                right1 = tile1.right(tr1)
                down1 = tile1.down(tr1)
                for tile2_number in neighbours:
                    tile2 = self.all_tiles[tile2_number]
                    for tr2_index, tr2 in enumerate(Matrix2x2.all_transformations()):
                        selection2 = TileSelection(tile2_number, tr2_index)
                        if right1 == tile2.left(tr2):  # tile2 in current transformation might be right to tile1
                            self.safe_add_to_dict_of_sets(self.right_successors, selection1, selection2)
                        if down1 == tile2.up(tr2):  # tile2 in current transformation might be under tile1
                            self.safe_add_to_dict_of_sets(self.down_successors, selection1, selection2)

    def stats(self):
        print("tiles with number of possible neighbours:")
        for td in self.tiles_with_degrees:
            print(f"{td.number}: {td.degree}")

    def possible_new_tiles_at_corner(self, chosen_numbers_set: Set[int], neighbours: List[TileNeighbour]) -> Iterable[TileSelection]:
        # this abuses given dataset property - there are exactly 4 tiles with degree 2,
        # to them, so they must be corners (tiles inside have more neighbours than 2)
        choices = (td.number for td in self.tiles_with_degrees[:4])
        yield from self.possible_new_tiles(choices, chosen_numbers_set, neighbours)

    def possible_new_tiles_at_border(self, chosen_numbers_set: Set[int], neighbours: List[TileNeighbour]) -> Iterable[TileSelection]:
        # similarly to possible_new_tiles_at_corner, this abuses dataset property -
        # there are exactly 40 tiles with degree 3 (and image is 12x12 tiles - border size excluding corners is 40),
        choices = (td.number for td in self.tiles_with_degrees[4:44])
        yield from self.possible_new_tiles(choices, chosen_numbers_set, neighbours)

    def possible_new_tiles_inside(self, chosen_numbers_set: Set[int], neighbours: List[TileNeighbour]) -> Iterable[TileSelection]:
        # this abuses properties of possible_new_tiles_at_corner and possible_new_tiles_inside
        choices = (td.number for td in self.tiles_with_degrees[44:])
        yield from self.possible_new_tiles(choices, chosen_numbers_set, neighbours)

    def possible_new_tiles(self, tile_number_choices: Iterable[int], chosen_numbers_set: Set[int], neighbours: List[TileNeighbour]) -> Iterable[TileSelection]:
        choice_filter = self.new_empty_filter()
        for n in neighbours:
            choice_filter = self.filter_by_neighbour(choice_filter, n)
        for number in tile_number_choices:
            if number in chosen_numbers_set:
                continue
            for tr_index, _ in enumerate(Matrix2x2.all_transformations()):
                selection = TileSelection(number, tr_index)
                if choice_filter(selection):
                    yield selection

    def filter_by_neighbour(self, current_filter: Callable[[TileSelection], bool], n: TileNeighbour) -> Callable[[TileSelection], bool]:
        if not n:  # there is no neighbour - no filter modification
            return current_filter
        successors_dict = getattr(self, n.direction_from_neighbour + "_successors")  # successor_direction must be right / up / left / down
        if n.neighbour not in successors_dict:  # there is neighbour with no allowed successors - filter will always fail
            return lambda selection: False
        available_selections = successors_dict[n.neighbour]
        return lambda selection: current_filter(selection) and selection in available_selections

    @staticmethod
    def new_empty_filter() -> Callable[[TileSelection], bool]:
        return lambda selection: True

    @staticmethod
    def safe_add_to_dict_of_sets(dictionary: Dict[object, Set[object]], key, value):
        if key not in dictionary:
            dictionary[key] = set()
        dictionary[key].add(value)


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

    def is_corner(self, x: int, y: int):
        return (x, y) in [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1)
        ]

    def is_border(self, x: int, y: int):
        return x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1


class MonsterParser:
    MONSTER = [
        "                  # ",
        "#    ##    ##    ###",
        " #  #  #  #  #  #   "
    ]

    def __init__(self):
        self.monster_width = len(self.MONSTER[0])
        self.monster_height = len(self.MONSTER)
        self.all_hashes = sum(line.count("#") for line in self.MONSTER)
        self.fields: Set[Tuple[int, int]] = set()
        for y, line in enumerate(self.MONSTER):
            for x, c in enumerate(line):
                if c == "#":
                    self.fields.add((x, y))

    def find_monster(self, data_source: Callable[[int, int], str], x_begin: int, y_begin: int) -> Set[Tuple[int, int]]:
        monster_fields: Set[Tuple[int, int]] = set()
        for f in self.fields:
            x, y = x_begin + f[0], y_begin + f[1]
            if data_source(x, y) != "#":
                return set()
            monster_fields.add((x, y))
        return monster_fields

    def count_monsters(self, data: List[str]) -> int:
        # I assume that monsters' bounding rectangles can overlap, but monster fields itself cannot,
        # so there is a set monster_fields - if some field is already in monster_fields, it cannot be used again
        monster_fields: Set[Tuple[int, int]] = set()
        count = 0
        y_end = len(data) - self.monster_height
        x_end = len(data[0]) - self.monster_width
        for y_begin in range(y_end):
            for x_begin in range(x_end):
                found = self.find_monster(lambda x, y: data[y][x] if (x, y) not in monster_fields else "", x_begin, y_begin)
                if len(found) > 0:
                    monster_fields.update(found)
                    count += 1
        return count


class Image:
    def __init__(self, tiles: List[Tile]):
        self.all_tiles: Dict[int, Tile] = {}
        for t in tiles:
            self.all_tiles[t.number] = t
        size = int(math.sqrt(len(tiles)))
        if size ** 2 != len(tiles):
            raise ValueError(f"number of tiles {len(tiles)} is not a square of natural number")
        self.indexer = ListToMatrixIndexer(size, size)
        self.choices: Dict[Tuple[int, int], TileSelection] = {}
        self.assembled_data: Tile = None
        self.all_hashes_count: int = 0

    # solve will try to put all tiles to their places so that they match.
    # On success it returns True and fills in self.choices dict
    # Otherwise it returns False
    def solve(self) -> bool:
        neighbourhood_manager = TileNeighbourhoodManager(self.all_tiles)
        self.choices = {}
        t1 = time.time()
        print(f"solving with backtracking for {len(self.all_tiles)} tiles ...")
        if self._solve(set(), neighbourhood_manager):
            t2 = time.time()
            print(f"solving with backtracking OK after {t2-t1}s")
            return True
        self.choices = {}  # reset choices
        return False

    def assemble(self):
        t1 = time.time()
        raw_data: List[str] = []
        for tile_y in range(self.indexer.height):
            for y_in_tile in itertools.chain(range(-4, 0), range(1, 5)):
                raw_data.append("".join(self._row_from_tile(tile_x, tile_y, y_in_tile) for tile_x in range(self.indexer.width)))
        expected_len = self.indexer.width * (HALF_TILE_LEN*2 - 2)
        if len(raw_data) != expected_len or len(raw_data[0]) != expected_len:
            raise RuntimeError(f"assemble assertion failed, expected square {expected_len}, got {len(raw_data[0])}x{len(raw_data)}")
        self.assembled_data = Tile(raw_data, 0)
        self.all_hashes_count = sum(line.count("#") for line in raw_data)
        t2 = time.time()
        print(f"assemble took {t2-t1}s")

    # magic number required as puzzle solution
    def find_sea_roughness(self) -> int:
        t1 = time.time()
        monsters_per_transformation: List[int] = []
        monster_parser = MonsterParser()
        for transformation in Matrix2x2.all_transformations():
            raw_data = self.assembled_data.all_data_as_list(transformation)
            monsters_per_transformation.append(monster_parser.count_monsters(raw_data))
        monsters = max(monsters_per_transformation)
        t2 = time.time()
        print(f"find_sea_roughness took {t2-t1}s, monsters {monsters_per_transformation} -> {monsters}")
        return self.all_hashes_count - monsters * monster_parser.all_hashes

    def _row_from_tile(self, tile_x, tile_y: int, y_in_tile: int) -> str:
        selection = self.choices[(tile_x, tile_y)]
        tile = self.all_tiles[selection.number]
        transformation = Matrix2x2.all_transformations()[selection.transformation_index]
        return tile.interior_row(y_in_tile, transformation)

    def _solve(self, chosen_numbers_set: Set[int], neighbourhood_manager: TileNeighbourhoodManager) -> bool:
        if len(self.choices) == len(self.all_tiles):
            return True
        x, y = self.indexer.coordinates(len(self.choices))
        neighbours = self._neighbours(x, y)
        if self.indexer.is_corner(x, y):
            possible_selections = neighbourhood_manager.possible_new_tiles_at_corner(chosen_numbers_set, neighbours)
        elif self.indexer.is_border(x, y):
            possible_selections = neighbourhood_manager.possible_new_tiles_at_border(chosen_numbers_set, neighbours)
        else:
            possible_selections = neighbourhood_manager.possible_new_tiles_inside(chosen_numbers_set, neighbours)
        for selection in possible_selections:
            # pick selection
            chosen_numbers_set.add(selection.number)
            self.choices[(x, y)] = selection
            # recursively try to fill in whole image
            if self._solve(chosen_numbers_set, neighbourhood_manager):
                return True
            # if recursive call failed, backtrack - revert choice and try other options
            del self.choices[(x, y)]
            chosen_numbers_set.remove(selection.number)
        return False  # there was no matching selection

    def _neighbours(self, x: int, y: int) -> List[TileNeighbour]:
        neighbours = []
        if x > 0:
            n = self.choices.get((x - 1, y))
            if n:
                neighbours.append(TileNeighbour(n, "right"))
        if y > 0:
            n = self.choices.get((x, y - 1))
            if n:
                neighbours.append(TileNeighbour(n, "down"))
        # we could also add left / up successors, but currently image is filled in left-to-right, up-down,
        # so newly added tile will never have neighbours above / to the left
        return neighbours


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
    image = Image(tiles)
    if not image.solve():
        print("could not find solution :(")
        return
    print("tiles combined together:")
    for y in range(image.indexer.height):
        for x in range(image.indexer.width):
            c = image.choices[(x, y)]
            print(f"({c.number} t{c.transformation_index})", end=" ")
        print("")
    image.assemble()
    print(f"final answer: {image.find_sea_roughness()}")


if __name__ == "__main__":
    main()
