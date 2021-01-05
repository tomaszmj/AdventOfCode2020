from typing import List
from functools import reduce


# Find gdc(a, b) (greatest common divisor) and x, y so that gcd = ax + by
def extended_euclidean_algorithm(a: int, b: int):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_euclidean_algorithm(b % a, a)
    x = y1 - (b//a) * x1
    y = x1
    return gcd, x, y


# Find smallest natural x matching system of congruences: x mod dividends[i] = remainders[i]
def chinese_remainder_algorithm(remainders: List[int], dividends: List[int]) -> int:
    if len(remainders) != len(dividends) or len(remainders) == 0:
        raise ValueError("invalid arguments for chinese remainder algorithm")
    m = [1] * len(remainders)
    m_inverse = [1] * len(remainders)
    dividends_product = reduce(lambda a, b: a*b, dividends)
    for i, n in enumerate(dividends):
        m[i] = dividends_product//n
        gdc, x, _ = extended_euclidean_algorithm(m[i], dividends[i])
        if gdc != 1:
            raise ValueError(f"Invalid input data for chinese remainder algorithm - at index {i} "
                             f"gcd({m[i]}, {dividends[i]}) = {gdc} (expected 1). "
                             f"Note that input dividends {dividends} should be relatively prime.")
        m_inverse[i] = x
    return sum((remainders[i] * m[i] * m_inverse[i] for i in range(len(remainders)))) % dividends_product


def main():
    with open("data.txt") as f:
        _ = int(f.readline().strip())
        buses = f.readline().strip().split(",")
    offsets: List[int] = []
    periods: List[int] = []
    for n, b in enumerate(buses):
        if b != "x":
            period = int(b)
            offsets.append((-n) % period)
            periods.append(period)
    timestamp = chinese_remainder_algorithm(offsets, periods)
    print(timestamp)


if __name__ == "__main__":
    main()
