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
    

def main():
    numbers: List[int] = []
    with open("data.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    print(f"first number that does not have summing property: {find_special_number(numbers)}")


if __name__ == "__main__":
    main()
