from typing import List, Set, Tuple


class Game:
    total_games = 0

    def __init__(self, p1: List[int], p2: List[int], triggered_by: int):
        self.p1 = p1
        self.p2 = p2
        self.record: Set[Tuple[Tuple[int], Tuple[int]]] = set()
        Game.total_games += 1
        self.number = Game.total_games
        self.triggered_by = triggered_by
        self.round = 0

    def play(self) -> int:
        #print(f"starting {self.describe()} with {self.p1} {self.p2}")
        while True:
            self.round += 1
            if not self._record_state():
                # "if there was a previous round in this game that had exactly the same cards in the
                # same order in the same players' decks, the game instantly ends in a win for player 1"
                #print(self.describe_winner(1))
                return 1
            self._play_round()
            if len(self.p1) == 0:
                #print(self.describe_winner(2))
                return 2
            elif len(self.p2) == 0:
                #print(self.describe_winner(1))
                return 1

    def score_winner(self, number: int) -> int:
        if number == 1:
            cards = self.p1
        elif number == 2:
            cards = self.p2
        else:
            raise ValueError(f"cannot score winner number {number}")
        multiplier = len(cards)
        return sum((multiplier - i) * card for i, card in enumerate(cards))

    def describe(self) -> str:
        return f"game {self.number} (subgame of {self.triggered_by})"

    def describe_winner(self, winner: int):
        return f"{self.describe()} ends with winner {winner} after {self.round} rounds with cards {self.p1} {self.p2}"

    def _record_state(self) -> bool:
        state = (tuple(self.p1), tuple(self.p2))
        if state in self.record:
            return False
        self.record.add(state)
        return True

    def _play_round(self):
        card1, card2 = self.p1.pop(0), self.p2.pop(0)
        winner = 0
        if len(self.p1) >= card1 and len(self.p2) >= card2:
            new_game = Game(self.p1[:card1].copy(), self.p2[:card2].copy(), self.number)
            winner = new_game.play()
        else:
            if card2 > card1:
                winner = 2
            elif card1 > card2:
                winner = 1
        if winner == 1:
            self.p1.extend((card1, card2))
        elif winner == 2:
            self.p2.extend((card2, card1))
        else:
            raise RuntimeError("draw in combat is not supported")
        #print(f"{self.describe()} round {self.round} -> {winner}")


def main():
    p1 = []
    p2 = []
    with open("data.txt") as f:
        line = f.readline().strip()
        if line != "Player 1:":
            raise ValueError("invalid data")
        line = f.readline().strip()
        while line:
            p1.append(int(line))
            line = f.readline().strip()
        line = f.readline().strip()
        if line != "Player 2:":
            raise ValueError("invalid data")
        line = f.readline().strip()
        while line:
            p2.append(int(line))
            line = f.readline().strip()
    game = Game(p1, p2, 0)
    winner = game.play()
    print(f"winner is {winner} with score {game.score_winner(winner)}")


if __name__ == "__main__":
    main()
