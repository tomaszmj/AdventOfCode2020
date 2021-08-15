from collections import deque


class Game:
    def __init__(self, data: str):
        self.data = deque(int(c) for c in data)
        self.datalen = len(self.data)
        if sorted(self.data) != list(range(1, self.datalen+1)):
            raise ValueError(f"expected natural numbers from 1 to {self.datalen}, got {data}")
        self.picked = [0]*3

    def play(self, iterations: int):
        for _ in range(iterations):
            current_item = self.data[0]
            self.rotate_item_at_the_end(current_item)
            for i in range(3):
                self.picked[i] = self.data.popleft()
            destination = self.select_destination(current_item)
            self.rotate_item_at_the_end(destination)
            for p in self.picked:
                self.data.append(p)
            self.rotate_item_at_the_end(current_item)

    def puzzle_answer(self) -> str:
        self.rotate_item_at_the_end(1)
        return "".join(f"{d}" for d in list(self.data)[:-1])

    def rotate_item_at_the_end(self, item: int):
        while self.data[-1] != item:
            self.data.rotate(-1)

    def select_destination(self, current_item: int) -> int:
        x = current_item - 1
        if x == 0:
            x = self.datalen
        while x in self.picked:
            x -= 1
            if x == 0:
                x = self.datalen
        return x


def solve(data: str, iterations: int):
    game = Game(data)
    game.play(iterations)
    print(game.puzzle_answer())


if __name__ == "__main__":
    solve("716892543", 100)
