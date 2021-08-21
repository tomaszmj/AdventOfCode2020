from typing import Tuple, Set, Iterable

# Directions of neighbours of a tile:
#      /\
#  ne /  \ nw
#    /    \
#   |      |
# e |      | w
#   |      |
#    \    /
#  se \  / sw
#      \/
# Tile is a hexagon. Let's set the length of tile side = 1,
# and Cartesian coordinates of initial tile center: (0, 0).
# Neighbours' centers are at coordinates:
# w = (sqrt(3), 0)
# e = (-sqrt(3), 0)
# nw = (sqrt(3)/2, 3/2)
# ne = (-sqrt(3)/2, 3/2)
# se = (-sqrt(3)/2, -3/2)
# sw = (sqrt(3)/2, -3/2)
# We are going to move only by multiple of the directions above.
# As you can see, x is always integer * (sqrt(3)/2), y is always integer * (3/2).
# To avoid losing precision during floating-point computations, we can substitute:
# a := sqrt(3) / 2
# b := 3/2
# x coordinate will be always multiple of a, y - multiple of b, so we can use the following simplified coordinates:
DIRECTIONS = {
    "e": (-2, 0),
    "se": (-1, -1),
    "sw": (1, -1),
    "w": (2, 0),
    "nw": (1, 1),
    "ne": (-1, 1),
}
# When considering coordinate range [min_x, min_y], [max_x, max_y] for many tiles,
# tiles can be enumerates as follows:
# y will be each integer from min_y to max_y
# x will be:
# - for y % 2 == 0 every even number between min_x and max_x
# - for y % 2 == 1 every odd number between min_x and max_x
# so simply: x % 2 == y % 2 


# parse_direction returns one of the DIRECTIONS above and remaining text, raises expection if text cannot be parsed
def parse_direction(text: str) -> Tuple[Tuple[int, int], str]:
    for name, value in DIRECTIONS.items():
        if text.startswith(name):
            return value, text[len(name):]
    raise ValueError(f"cannot parse direction from {text}")


def count_black_neighbours(black_tiles: Set[Tuple[int, int]], coords: Tuple[int, int]) -> int:
    count = 0
    for dx, dy in DIRECTIONS.values():
        x = coords[0] + dx
        y = coords[1] + dy
        if (x, y) in black_tiles:
            count += 1
    return count


# Space of tiles is infinite. Tiles by default are white.
# In tiles_game_of_life something may change in a tile if
# it is black or if it has black neighbours.
# SpaceChecker determines what tiles have to be checked.
# Previously it determined range [min_x, max_x] and [min_y, max_y]
# according to description below DIRECTIONS, but this approach is simpler.
class SpaceChecker:
    def __init__(self) -> None:
        self.to_check: Set[Tuple[int, int]] = set()

    def update(self, position: Tuple[int, int]):
        self.to_check.add(position)
        for dx, dy in DIRECTIONS.values():
            x = position[0] + dx
            y = position[1] + dy
            self.to_check.add((x, y))

    def all_elements_to_check(self) -> Iterable[Tuple[int, int]]:
        return self.to_check


def tiles_game_of_life(black_tiles: Set[Tuple[int, int]], iterations: int) -> Set[Tuple[int, int]]:
    space = SpaceChecker()
    for position in black_tiles:
        space.update(position)
    for i in range(iterations):
        new_black_tiles = set()
        new_space = SpaceChecker()
        for position in space.all_elements_to_check():
            neighbours = count_black_neighbours(black_tiles, position)
            if position in black_tiles:  # tile under position is black
                # Any black tile with zero or more than 2 black tiles immediately adjacent to it is flipped to white.
                if neighbours == 0 or neighbours > 2:
                    pass  # tile changes to white (we write only black ones)
                else:
                    new_black_tiles.add(position)  # tile remains black
                    new_space.update(position)
            else:  # tile under position is white
                # Any white tile with exactly 2 black tiles immediately adjacent to it is flipped to black.
                if neighbours == 2:
                    new_black_tiles.add(position)  # write new black tile
                    new_space.update(position)
                else:
                    pass  # tile remains white (we write only black ones)
        # print(f"Day {i+1}: black tiles {len(new_black_tiles)}, " +
        #       f"x range {new_border.min[0]}:{new_border.max[0]}, " + 
        #       f"y range {new_border.min[1]}:{new_border.max[1]}"
        #     )
        space = new_space
        black_tiles = new_black_tiles
    return black_tiles
    


def main():
    black_tiles: Set[Tuple[int, int]] = set()
    with open("data.txt") as f:
        for line in f:
            x, y = 0, 0
            text = line.strip()
            while text:
                direction, remaining_text = parse_direction(text)
                text = remaining_text
                x += direction[0]
                y += direction[1]
            if (x, y) in black_tiles:
                black_tiles.remove((x, y))
            else:
                black_tiles.add((x, y))
    print(len(tiles_game_of_life(black_tiles, 100)))


if __name__ == "__main__":
    main()
