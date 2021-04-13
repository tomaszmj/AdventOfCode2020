from typing import Dict, List


def record_number(record: Dict[int, List[int]], turn: int, number: int):
    if number not in record:
        record[number] = [turn]
    else:
        prev = record[number][-1]
        record[number] = [prev, turn]


def game(turns: int, data: List[int]) -> int:
    record = {}  # key: spoken number, value: turns in which number was spoken (max 2 last ones)
    for i, n in enumerate(data):
        record_number(record, i + 1, n)  # i + 1 because we want to count turns from 1, same as in puzzle description
    last_spoken = data[-1]
    for i in range(len(data) + 1, turns + 1):
        if len(record[last_spoken]) == 1:
            last_spoken = 0
        else:
            last_spoken = record[last_spoken][-1] - record[last_spoken][-2]
        record_number(record, i, last_spoken)
    return last_spoken


def main():
    with open("data.txt") as f:
        data = list(int(n) for n in f.readline().split(","))
    print(f"part1: number after 2020 turns: {game(2020, data)}")
    print(f"part2: number after 30000000 turns: {game(30000000, data)}")


if __name__ == "__main__":
    main()
