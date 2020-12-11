import itertools
from typing import List


def check_if_numbers_sum_up(numbers: List[int], sum: int):
    for pair in itertools.combinations(numbers, r=2):
        if pair[0] + pair[1] == sum and pair[0] != pair[1]:
            return True
    return False


def find_special_number(numbers: List[int]):
    for i in range(25, len(numbers)):
        if not check_if_numbers_sum_up(numbers[i-25:i], numbers[i]):
            return numbers[i]


def find_summing_sequence(numbers: List[int], sum: int) -> (int, int):
    for i in range(len(numbers) - 1):
        current_sum = numbers[i]
        for j in range(i+1, len(numbers)):
            current_sum += numbers[j]
            if current_sum == sum:
                return i, j
            if current_sum > sum:
                break
    raise RuntimeError(f"could not find a subsequence that sums up to {sum}")
    

def main():
    numbers: List[int] = []
    with open("data.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    special_number = find_special_number(numbers)
    begin, end = find_summing_sequence(numbers, special_number)
    summing_sequence = numbers[begin:end+1]
    print(f"XMAS encryption weakness: {min(summing_sequence) + max(summing_sequence)}")


if __name__ == "__main__":
    main()
