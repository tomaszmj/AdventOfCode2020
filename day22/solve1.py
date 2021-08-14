from typing import List


def play_round(p1: List[int], p2: List[int]):
    card1, card2 = p1.pop(0), p2.pop(0)
    if card1 == card2:
        raise RuntimeError("draw in combat is not supported")
    if card2 > card1:
        p2.extend((card2, card1))
    else:
        p1.extend((card1, card2))


def score(cards: List[int]) -> int:
    multiplier = len(cards)
    return sum((multiplier - i) * card for i, card in enumerate(cards))


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
    while True:
        play_round(p1, p2)
        if len(p1) == 0:
            winner = ("2", p2)
            break
        elif len(p2) == 0:
            winner = ("1", p1)
            break
    print(f"winner - player {winner[0]}, with score {score(winner[1])}")


if __name__ == "__main__":
    main()
