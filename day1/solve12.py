# I started AoC in Go, then decided to move to Python for convenience
# (mostly beceuse parsing input data is much more elegant). After
# finishing all puzzles, I re-wrote solution for day1 in Python for cohesion.
from typing import List
import itertools
import math


def solve1(numbers: List[int]) -> int:
    for chosen in itertools.combinations(numbers, 2):
        if sum(chosen) == 2020:
            return math.prod(chosen)
    raise RuntimeError("no numbers found")


def solve2(numbers: List[int]) -> int:
    for chosen in itertools.combinations(numbers, 3):
        if sum(chosen) == 2020:
            return math.prod(chosen)
    raise RuntimeError("no numbers found")


def main():
    with open("data1.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    print(f"part1: {solve1(numbers)}")
    print(f"part2: {solve2(numbers)}")


if __name__ == "__main__":
    main()