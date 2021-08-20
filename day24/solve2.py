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


class Border:
    def __init__(self) -> None:
        self.min = [0, 0]
        self.max = [-1, -1]  # space is from min to max (inclusive), min < max indicates 0 size - similar idea as in day17

    def update(self, position: Tuple[int, int]):
        self.min[0] = min(position[0], self.min[0])
        self.min[1] = min(position[1], self.min[1])
        self.max[0] = max(position[0], self.max[0])
        self.max[1] = max(position[1], self.max[1])

    def all_elements_with_margin(self) -> Iterable[Tuple[int, int]]:
        # extend range by 1 in both directions to include potential new tiles below / above
        for y in range(self.min[1] - 1, self.max[1] + 2):
            mod = y % 2
            # Extend range by 2 in both directions to include potential new tiles left / right
            # (by 2 because of how x coordinates are laid out - see comment below DIRECTIONS)
            # Maybe we are including some redundant elements here, but that's not a problem -
            # iterating them all does not hurt correctness (only performance a bit), because space is infinite.
            for x in range(self.min[0] - 2, self.max[0] + 3):
                if x % 2 == mod:
                    yield (x, y)


def tiles_game_of_life(black_tiles: Set[Tuple[int, int]], iterations: int) -> Set[Tuple[int, int]]:
    border = Border()
    for position in black_tiles:
        border.update(position)
    tlist = [black_tiles.copy(), set()]
    for i in range(iterations):
        src = tlist[i%2]
        dst = tlist[(i+1)%2]
        new_border = Border()
        for position in border.all_elements_with_margin():
            neighbours = count_black_neighbours(src, position)
            if position in src:  # tile under position is black
                # Any black tile with zero or more than 2 black tiles immediately adjacent to it is flipped to white.
                if neighbours == 0 or neighbours > 2:
                    dst.discard(position)  # tile changes to white (discard to override content from previous iterations if needed)
                else:
                    dst.add(position)  # tile remains black
                    new_border.update(position)
            else:  # tile under position is white
                # Any white tile with exactly 2 black tiles immediately adjacent to it is flipped to black.
                if neighbours == 2:
                    dst.add(position)  # write new black tile
                    new_border.update(position)
                else:
                    dst.discard(position)  # tile remains white (discard to override content from previous iterations if needed)
        border = new_border
        # print(f"Day {i+1}: black tiles {len(dst)}, " +
        #       f"x range {new_border.min[0]}:{new_border.max[0]}, " + 
        #       f"y range {new_border.min[1]}:{new_border.max[1]}"
        #     )
    return tlist[(iterations - 1 + 1) % 2]  # return dst from last iteration
    


# Note: in puzzle description for example data (data_small.txt) there is an answer not matching what my code produces:
# after 100 days: 2208, in my code it is 2136 (the first 9 days are the same, difference is from day 10: my 39, example 37).
# The program works for full dataset - it produced correct answer 3964.
# I spent some time debugging if there is a bug here despite correct answer, but I could not find one.
# Still I am not sure if there was a bug in the example answer or if my solution does not work for some corner cases.
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
