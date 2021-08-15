from typing import List


class Game:
    def __init__(self, data: str, total_len: int):
        data = list(int(c) for c in data)
        if sorted(data) != list(range(1, len(data)+1)):
            raise ValueError(f"expected natural numbers from 1 to {len(data)}, got {data}")
        if total_len < len(data):
            raise ValueError(f"invalid total_len ({total_len}) for len(data) ({len(data)})")
        # followers[a] = b -> it means that b is after a in the list.
        # It is another way of storing the circle of numbers, which allows to lookup numbers in O(1).
        # followers[0] will be unused - for simplicity of implementation I want to use 1-based indexing here.
        self.followers = [0] * (total_len + 1)
        for first, second in zip(data[:-1], data[1:]):  # links between given elements: 1, 2, ..., len(data)-1
            self.followers[first] = second
        if total_len == len(data):  # for compatibility with part1 (to verify correctness)
            self.followers[data[-1]] = data[0]  # link between last given element and first given element
        else:  # normal case for part2 - there are more elements than just given data
            self.followers[data[-1]] = len(data) + 1  # link between last given element and first generated
            for x in range(len(data) + 1, total_len):  # links between generated elements
                self.followers[x] = x + 1
            self.followers[total_len] = data[0]  # link between last generated element and first given
        self.picked = [0]*3
        self.datalen = total_len
        self.current_item = data[0]

    def all_elements(self, starting_at: int) -> List[int]:  # used only for tests
        current = starting_at
        retval = []
        used = set()
        while current not in used:
            used.add(current)
            retval.append(current)
            current = self.followers[current]
        return retval

    def play(self, iterations: int):
        for _ in range(iterations):
            #print(self.all_elements(self.current_item), end=" -> ")
            # move 3 items after current_item to picked list:
            current = self.current_item
            for i in range(3):
                current = self.followers[current]
                self.picked[i] = current
            self.followers[self.current_item] = self.followers[self.picked[-1]]  # virtually remove picked items
            # find destination for picked items:
            destination = self.select_destination(self.current_item)
            #print(f"picked {self.picked}, destination {destination} -> {self.all_elements(self.current_item)} -> ", end="")
            # add previously removed items after destination
            after_destination = self.followers[destination]
            for p in self.picked:
                self.followers[destination] = p
                destination = p
            self.followers[self.picked[-1]] = after_destination
            # advance current_item
            #print(self.all_elements(self.current_item))
            self.current_item = self.followers[self.current_item]

    def puzzle_answer1(self) -> str:  # for compatibility with part1 (to verify correctness)
        data = self.all_elements(1)
        return "".join(f"{d}" for d in data[1:])

    def puzzle_answer2(self) -> int:
        after1 = self.followers[1]
        afterafter1 = self.followers[after1]
        return after1 * afterafter1

    def select_destination(self, current_item: int) -> int:
        x = current_item - 1
        if x == 0:
            x = self.datalen
        while x in self.picked:
            x -= 1
            if x == 0:
                x = self.datalen
        return x


def main():
    game = Game("716892543", 10**6)
    game.play(10**7)
    print(game.puzzle_answer2())


if __name__ == "__main__":
    main()
