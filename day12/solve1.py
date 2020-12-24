import math


class Instruction:
    def __init__(self, line: str):
        if len(line) < 2:
            raise ValueError(f'cannot create instruction from line "{line}"')
        if line[0] not in "NSEWLRF":
            raise ValueError(f'cannot create instruction from line "{line}"')
        self.type = line[0]
        try:
            self.value = int(line[1:])
        except ValueError:
            raise ValueError(f'cannot create instruction from line "{line}"')


# Coordinate system:
#     N
#     ^
#     |
# W --+--> E
#     |
#     S
# That is, north is positive y, east is positive x, angle is counter-clockwise from positive x axis
class Ship:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0

    def execute(self, i: Instruction):
        if i.type == "N":
            self.y += i.value
        elif i.type == "S":
            self.y -= i.value
        elif i.type == "E":
            self.x += i.value
        elif i.type == "W":
            self.x -= i.value
        elif i.type == "L":
            self.angle += i.value
            if self.angle > 360:
                self.angle -= 360
        elif i.type == "R":
            self.angle -= i.value
            if self.angle < 0:
                self.angle += 360
        elif i.type == "F":
            self.x += i.value * math.cos(math.radians(self.angle))
            self.y += i.value * math.sin(math.radians(self.angle))

    def manhattan_distance_from_start(self) -> float:
        return math.fabs(self.x) + math.fabs(self.y)


def main():
    ship = Ship()
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if line:
                ship.execute(Instruction(line))
    print(ship.manhattan_distance_from_start())


if __name__ == "__main__":
    main()
