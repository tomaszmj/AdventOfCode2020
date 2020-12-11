import itertools
from typing import List


def main():
    numbers: List[int] = []
    with open("data.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    diffs = {0: 0, 1: 0, 2: 0, 3: 1}
    numbers.sort()
    diffs[numbers[0]] = 1
    for i in range(len(numbers) - 1):
        diff = numbers[i+1] - numbers[i]
        if diff > 3:
            raise RuntimeErorr("difference larger than 3")
        diffs[diff] += 1
    print(f"result: {diffs[1] * diffs[3]}")


if __name__ == "__main__":
    main()
