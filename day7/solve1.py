from typing import List, Dict, NamedTuple, Set


class BagContainsStatement(NamedTuple):
    name: str
    amount: int


class ParsedInputLine:
    class ParseException(Exception):
        def __init__(self, line: str, parent_exception: Exception):
            super().__init__(f'error parsing line "{line}" : {str(parent_exception)}')

    def __init__(self, line: str):
        try:
            line_split = line.split(" ")
            self.bag_name = " ".join(line_split[:2])
            self.contain_list = self._read_contain_list(line_split[4:])
        except Exception as e:
            raise self.ParseException(line, e)

    def _read_contain_list(self, contain_list_str: List[str]) -> List[BagContainsStatement]:
        contain_list: List[BagContainsStatement] = []
        if " ".join(contain_list_str) == "no other bags.":
            return contain_list
        for i in range(0, len(contain_list_str), 4):
            amount = int(contain_list_str[i])
            name = contain_list_str[i+1] + " " + contain_list_str[i+2]
            contain_list.append(BagContainsStatement(name, amount))
        return contain_list

    def __str__(self):
        return self.bag_name + " bag can contain: " + ", ".join(str(s) for s in self.contain_list)


class BagSet:
    def __init__(self):
        self.bags: Dict[str, List[BagContainsStatement]] = {}

    def add(self, data: ParsedInputLine):
        if data.bag_name in self.bags:
            print(f"warning - bag {data.bag_name} is already in the set")
            return
        self.bags[data.bag_name] = data.contain_list

    def find_possible_parents(self, child: str) -> Set[str]:
        return self._find_possible_parents_internal(child, {child})

    def _find_possible_parents_internal(self, child: str, forbidden_parents: Set[str]) -> Set[str]:
        possible_parents = set()
        for bag_name, bag_children in self.bags.items():
            if bag_name in forbidden_parents:
                continue
            if child in (c.name for c in bag_children):
                possible_parents.add(bag_name)
                forbidden_parents.add(bag_name)
        parents1 = set()
        for parent0 in possible_parents:
            parents1 = parents1.union(self._find_possible_parents_internal(parent0, forbidden_parents))
        possible_parents = possible_parents.union(parents1)
        return possible_parents


def main():
    bag_set = BagSet()
    checked_bag = "shiny gold"
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            parsed_line = ParsedInputLine(line)
            bag_set.add(parsed_line)
    print(f"possible outermost parents of {checked_bag}: {len(bag_set.find_possible_parents(checked_bag))}")


if __name__ == "__main__":
    main()
