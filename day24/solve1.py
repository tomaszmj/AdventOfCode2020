from collections import defaultdict
from typing import Tuple, Dict

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


# parse_direction returns one of the DIRECTIONS above and remaining text, raises expection if text cannot be parsed
def parse_direction(text: str) -> Tuple[Tuple[int, int], str]:
    for name, value in DIRECTIONS.items():
        if text.startswith(name):
            return value, text[len(name):]
    raise ValueError(f"cannot parse direction from {text}")


def defaultdict_factory() -> str:
    return "white"


def main():
    tiles: Dict[Tuple[int, int], str] = defaultdict(defaultdict_factory)
    total_black = 0
    with open("data.txt") as f:
        for line in f:
            x, y = 0, 0
            text = line.strip()
            while text:
                direction, remaining_text = parse_direction(text)
                text = remaining_text
                x += direction[0]
                y += direction[1]
            if tiles[(x, y)] == "white":
                tiles[(x, y)] = "black"
                total_black += 1
            else:
                tiles[(x, y)] = "white"
                total_black -= 1
    #print("\n".join(f"{coords}: {colour}" for coords, colour in tiles.items()))
    print(total_black)


if __name__ == "__main__":
    main()
