from typing import List, Iterable


def yield_subsets(numbers: List[int]) -> Iterable[List[int]]:
    for subset_id in range(2**len(numbers)):
        retval = []
        for i in range(len(numbers)):
            if subset_id & (1<<i):
                retval.append(numbers[i])
        yield retval


def is_correct(numbers: Iterable[int]) -> bool:
    last = 0
    for n in numbers:
        if n - last > 3 or n - last < 0:
            return False
        last = n
    return True


def split_into_unremovable_and_removable(numbers: List[int]) -> (List[int], List[int]):
    unremovable = []
    removable = []
    for i, n in enumerate(numbers):
        prev = numbers[i - 1] if i > 0 else 0
        next = numbers[i + 1] if i < len(numbers) - 1 else n + 3
        if n - prev == 3 or next - n == 3:
            unremovable.append(i)
        else:
            removable.append(i)
    return unremovable, removable


def numbers_subset(numbers: List[int], removed_indices: List[int]) -> Iterable[int]:
    r = 0
    for i, n in enumerate(numbers):
        if r >= len(removed_indices):
            yield n
        elif removed_indices[r] == i:
            r += 1
        else:
            yield n


def brute_force_count(numbers: List[int]) -> int:
    #return functools.reduce(operator.add, (int(is_correct(s)) for s in yield_subsets(numbers)))
    count = 0
    for subset in yield_subsets(numbers):
        if is_correct(subset):
            count += 1
    return count


def solve(numbers: List[int]) -> int:
    numbers.sort()
    unremovable, removable = split_into_unremovable_and_removable(numbers)
    count = 0
    for removed_indices in yield_subsets(removable):
        if is_correct(numbers_subset(numbers, removed_indices)):
            count += 1
    return count
    

def main():
    numbers: List[int] = []
    with open("data_small.txt") as file:
        numbers = list(int(line.strip()) for line in file) 
    print(solve(numbers))


if __name__ == "__main__":
    main()
