from typing import List, Dict


class BagContainsStatement:
    def __init__(self, name: str, amount: int):
        self.name = name
        self.amount = amount

    def __str__(self):
        return f"{self.amount} {self.name}"


class Bag:
    def __init__(self):
        self.parents: List[int] = []
        self.children: List[BagContainsStatement] = []


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
        self.bags: Dict[str, Bag] = {}

    def add(self, data: ParsedInputLine):
        print(data)


def main():
    bag_set = BagSet()
    with open("data_small.txt") as f:
        for line in f:
            line = line.strip()
            parsed_line = ParsedInputLine(line)
            bag_set.add(parsed_line)


if __name__ == "__main__":
    main()
