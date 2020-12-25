from typing import List, NamedTuple


class Departure(NamedTuple):
    timestamp: int
    bus_number: int


def main():
    with open("data.txt") as f:
        current_timestamp = int(f.readline().strip())
        buses = f.readline().strip().split(",")
    bus_numbers = []
    for b in buses:
        if b != "x":
            bus_numbers.append(int(b))
    departures: List[Departure] = []
    for bus_number in bus_numbers:
        if current_timestamp % bus_number == 0:
            departures.append(Departure(current_timestamp, bus_number))
        else:
            bus_periods = (current_timestamp // bus_number) + 1
            departures.append(Departure(bus_periods * bus_number, bus_number))
    earliest_departure = min(departures, key=lambda d: d.timestamp)
    wait_time = earliest_departure.timestamp - current_timestamp
    print(f"earliest departure at {earliest_departure.timestamp} with bus {earliest_departure.bus_number}, "
          f"multiply result (wait_time * bus_number) {wait_time * earliest_departure.bus_number}")


if __name__ == "__main__":
    main()
