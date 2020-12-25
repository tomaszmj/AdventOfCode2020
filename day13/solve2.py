from typing import List, NamedTuple


class Departure(NamedTuple):
    offset: int
    period: int

    def occurs_at(self, base_timestamp: int) -> bool:
        return (base_timestamp + self.offset) % self.period == 0


def departures_occur_with_proper_offsets(departures: List[Departure], base_timestamp: int):
    for d in departures:
        if not d.occurs_at(base_timestamp):
            return False
    return True


def main():
    with open("data.txt") as f:
        _ = int(f.readline().strip())
        buses = f.readline().strip().split(",")
    departures: List[Departure] = []
    for n, b in enumerate(buses):
        if b != "x":
            departures.append(Departure(n, int(b)))
    timestamp = 0
    while not departures_occur_with_proper_offsets(departures[1:], timestamp):
        timestamp += departures[0].period
    print(timestamp)


if __name__ == "__main__":
    main()
