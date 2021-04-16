from typing import List, Dict


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


class RuleMatcher:
    def __init__(self, index: int):
        self.index: int = index
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)


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
        neighbour_codes = list((int(n) for n in line.split(",")))
        if len(neighbour_codes) != len(self.own_codes):
            raise ValueError(f"cannot add neighbour with {len(neighbour_codes)} codes,"
                             f" expected {len(self.own_codes)} codes")
        self.neighbours.append(neighbour_codes)

    def __str__(self) -> str:
        return "rules:\n" + "\n".join(str(r) for r in self.rules) + f"\ncodes: {self.own_codes}\n" +\
               "nearby codes:\n" + "\n".join(str(r) for r in self.neighbours) + "\n"

    def discard_invalid_neighbours(self):
        def code_matches_any_rule(code: int) -> bool:
            return any(rule.matches_code(code) for rule in self.rules)

        def neighbour_is_valid(neighbour_codes: List[int]) -> bool:
            return all(code_matches_any_rule(code) for code in neighbour_codes)

        self.neighbours = list(filter(neighbour_is_valid, self.neighbours))

    def possible_rules(self) -> List[RuleMatcher]:
        possible_rules: List[RuleMatcher] = []
        for index in range(len(self.own_codes)):
            matcher = RuleMatcher(index)
            for rule in self.rules:
                if all(rule.matches_code(c) for c in (neighbour_codes[index] for neighbour_codes in self.neighbours)):
                    matcher.add_rule(rule)
            possible_rules.append(matcher)
        return possible_rules

    def match_rules(self) -> Dict[str, int]:
        possible_rules = self.possible_rules()
        possible_rules.sort(key=lambda matcher: len(matcher.rules))
        used_names = set()
        names_to_indices: Dict[str, int] = {}
        for matcher in possible_rules:
            possible_matches = []
            for rule in matcher.rules:
                if rule.name not in used_names:
                    possible_matches.append(rule)
            if len(possible_matches) != 1:
                raise RuntimeError(f"Cannot match rules at index {matcher.index}, expected exactly 1 match, "
                                   f"got {possible_matches}")
            used_names.add(possible_matches[0].name)
            names_to_indices[possible_matches[0].name] = matcher.index
        return names_to_indices

    def get_code(self, index: int):
        return self.own_codes[index]


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
    ticket.discard_invalid_neighbours()
    matches = ticket.match_rules()
    product = 1
    for name, index in matches.items():
        if name.startswith("departure"):
            product *= ticket.get_code(index)
    print(product)


if __name__ == "__main__":
    main()
