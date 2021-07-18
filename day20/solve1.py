import math
from typing import Dict, List, NamedTuple, Set


class Tile:
    def __init__(self, text: List[str]):
        # Borders of tile, starting at upper left corner, going clockwise:
        # up in direction left->right
        # right in direction up->down
        # down in direction right->left
        # left in direction down->up
        self._borders = [
            text[0],
            "".join((t[-1] for t in text)),  # last character from each line
            text[-1][::-1],  # reversed last line
            "".join((t[0] for t in reversed(text))),  # first character from each line, reversed because we start from bottom
        ]

    # up, right, down, left are getters for tile borders
    # They take rotation as parameter so that Tile can be viewed as rotated without being modified
    # rotation is number of clockwise rotations by 1, i.e. rotation=1 transforms up to right, right to down etc.

    def up(self, rotation=0) -> str:
        return self._borders[(0 - rotation) % 4]

    def right(self, rotation=0) -> str:
        return self._borders[(1 - rotation) % 4]

    def down(self, rotation=0) -> str:
        return self._borders[(2 - rotation) % 4]

    def left(self, rotation=0) -> str:
        return self._borders[(3 - rotation) % 4]


class TileDescriptor(NamedTuple):
    number: int
    rotation: int


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


class Image:
    def __init__(self, tiles: Dict[int, Tile]):
        self.all_tiles = tiles
        size = int(math.sqrt(len(tiles)))
        if size ** 2 != len(tiles):
            raise ValueError(f"number of tiles {len(tiles)} is not a square of natural number")
        self.indexer = ListToMatrixIndexer(size, size)

    # solve will try to put all tiles to their places so that they math.
    # It returns list of chosen tile descriptors (number, rotation) on success, empty list on failure
    def solve(self) -> List[TileDescriptor]:
        chosen_tiles: List[TileDescriptor] = []
        if self._solve(chosen_tiles, set()):
            return chosen_tiles
        return []

    def _solve(self, chosen_tiles: List[TileDescriptor], chosen_numbers_set: Set[int]) -> bool:
        print(f"_solve({self.chosen_tiles_to_string(chosen_tiles)}) ...")
        if len(chosen_tiles) == len(self.all_tiles):
            return True
        # We iterate over all possible tiles numbers, filtered by chosen_numbers_set instead of just
        # using available numbers set, because we cannot add/remove items to the set while iterating over it
        for tile_number in self.all_tiles.keys():
            if tile_number in chosen_numbers_set:
                continue
            chosen_numbers_set.add(tile_number)
            for rotation in range(4):
                new_tile_descriptor = TileDescriptor(tile_number, rotation)
                if self.new_tile_matches(chosen_tiles, new_tile_descriptor):
                    chosen_tiles.append(new_tile_descriptor)
                    if self._solve(chosen_tiles, chosen_numbers_set):
                        return True
                    chosen_tiles.pop()
            chosen_numbers_set.remove(tile_number)
        return False

    def new_tile_matches(self, chosen_tiles: List[TileDescriptor], new_tile_descriptor: TileDescriptor) -> bool:
        new_x, new_y = self.indexer.coordinates(len(chosen_tiles))
        new_tile = self.all_tiles[new_tile_descriptor.number]
        if new_x > 0:
            left_neighbour_index = self.indexer.list_index(new_x - 1, new_y)
            left_neighbour = chosen_tiles[left_neighbour_index]
            left_neighbour_right_border = self.all_tiles[left_neighbour.number].right(left_neighbour.rotation)
            new_tile_left_border = new_tile.left(new_tile_descriptor.rotation)
            # left border is up->down oriented, right border is down->up, so check if borders are equal in reversed order
            if new_tile_left_border[::-1] != left_neighbour_right_border:
                return False
        if new_y > 0:
            up_neighbour_index = self.indexer.list_index(new_x, new_y - 1)
            up_neighbour = chosen_tiles[up_neighbour_index]
            up_neighbour_down_border = self.all_tiles[up_neighbour.number].down(up_neighbour.rotation)
            new_tile_up_border = new_tile.up(new_tile_descriptor.rotation)
            # up border is left->right oriented, down border is right->left, so check if borders are equal in reversed order
            if new_tile_up_border[::-1] != up_neighbour_down_border:
                return False
        # we are putting new tiles left-to-right, up-down, so new tile will never have neighbours right or down
        return True

    @staticmethod
    def chosen_tiles_to_string(chosen_tiles: List[TileDescriptor]) -> str:
        return " ".join(f"{c.number},{c.rotation}" for c in chosen_tiles)


def main():
    tiles: Dict[int, Tile] = {}
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
            tiles[number] = Tile(data)
            line = f.readline().strip()
            if line:
                raise ValueError(f"expected empty line, got {line}")
            line = f.readline().strip()
    # t = tiles[2311]
    # full_text = "\n".join(t.text)
    # print(f"full text:\n{full_text}")
    # for rot in range(5):
    #     print(f"\nrotation {rot}\nup: {t.up(rot)}\nright: {t.right(rot)}\ndown: {t.down(rot)}\nleft: {t.left(rot)}")
    image = Image(tiles)
    chosen_tiles = image.solve()
    print(f"solution [{Image.chosen_tiles_to_string(chosen_tiles)}]")


if __name__ == "__main__":
    main()
