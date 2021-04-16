from typing import List


class Rule:
    def __init__(self, text: str):
        name_end = text.find(":")
        if name_end < 0:
            raise ValueError(f"cannot create Rule from line '{text}'")
        self.name = text[:name_end]
        ranges_str = text[(name_end+1):].split()
        self.ranges = []
        for r in ranges_str:
            if r == "or":
                continue
            self.ranges.extend(int(s) for s in r.split("-"))
        if len(self.ranges) != 4:
            raise ValueError(f"cannot create Rule from line '{text}' - expected 4 range numbers")
        if not (self.ranges[0] < self.ranges[1] < self.ranges[2] < self.ranges[3]):
            raise ValueError(f"cannot create Rule from line '{text}' - range numbers are not sorted")

    def __str__(self) -> str:
        return f"{self.name} {self.ranges}"

    def matches_code(self, code: int) -> bool:
        return (self.ranges[0] <= code <= self.ranges[1]) or (self.ranges[2] <= code <= self.ranges[3])


class Ticket:
    def __init__(self):
        self.rules: List[Rule] = []
        self.own_codes: List[int] = []
        self.neighbours: List[List[int]] = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def set_own_codes(self, line: str):
        self.own_codes = list((int(n) for n in line.split(",")))

    def add_neighbour(self, line: str):
        self.neighbours.append(list((int(n) for n in line.split(","))))

    def __str__(self) -> str:
        return "rules:\n" + "\n".join(str(r) for r in self.rules) + f"\ncodes: {self.own_codes}\n" +\
               "nearby codes:\n" + "\n".join(str(r) for r in self.neighbours) + "\n"

    def sum_invalid_values_in_neighbours(self) -> int:
        result = 0
        for ticket in self.neighbours:
            for code in ticket:
                if not any(rule.matches_code(code) for rule in self.rules):
                    result += code
        return result


def main():
    ticket = Ticket()
    with open("data.txt") as f:
        while True:
            line = f.readline().strip()
            if not line:
                break
            ticket.add_rule(Rule(line))
        line = f.readline().strip()
        if line != "your ticket:":
            raise ValueError(f"invalid data format, expected 'your ticket:' line, got {line}")
        ticket.set_own_codes(f.readline().strip())
        f.readline().strip()
        line = f.readline().strip()
        if line != "nearby tickets:":
            raise ValueError(f"invalid data format, expected 'nearby tickets:' line, got {line}")
        line = f.readline().strip()
        while line:
            ticket.add_neighbour(line)
            line = f.readline().strip()
    print(f"sum of invalid values: {ticket.sum_invalid_values_in_neighbours()}")


if __name__ == "__main__":
    main()
