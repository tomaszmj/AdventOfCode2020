import functools
import operator
from typing import List, Iterable


def yield_subsets(numbers: List[int]) -> Iterable[List[int]]:
    for subset_id in range(2**len(numbers)):
        retval = []
        for i in range(len(numbers)):
            if subset_id & (1<<i):
                retval.append(numbers[i])
        yield retval


def is_correct(numbers: List[int]) -> bool:
    if len(numbers) == 0:
        return False
    last_number = numbers[0]
    for n in numbers[1:]:
        if n - last_number > 3 or n - last_number < 0:
            return False
        last_number = n
    return True


# splits list into sublists divided by "unremovable" elements
# "unremovable" elements are the ones that have difference of 3 from one of neighbours
def split(numbers: List[int]) -> List[List[int]]:
    retval = []
    current_sublist = []
    for i, n in enumerate(numbers):
        prev = numbers[i - 1] if i > 0 else 0
        next = numbers[i + 1] if i < len(numbers) - 1 else n + 3
        if n - prev == 3 or next - n == 3:
            if len(current_sublist) > 0:
                retval.append(current_sublist)
                current_sublist = []
        else:
            current_sublist.append(i)
    return retval


def solve(numbers: List[int]) -> int:
    numbers.sort()
    #print(numbers, end="\n\n")
    count = 1
    for slice in split(numbers):
        prev = numbers[slice[0] - 1] if slice[0] > 0 else 0
        next = numbers[slice[-1] + 1] if slice[-1] < len(numbers) - 1 else numbers[-1] + 3
        fragment = list(numbers[s] for s in slice)
        subsets = yield_subsets(fragment)
        subsequence_count = functools.reduce(operator.add, (int(is_correct([prev] + s + [next])) for s in subsets))
        #print(f"({prev}) {fragment} ({next}) -> {subsequence_count}")
        count *= subsequence_count
    return count
    

def main():
    numbers: List[int] = []
    with open("data.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    print(solve(numbers))


if __name__ == "__main__":
    main()
