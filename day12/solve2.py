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
        self.wx = 10  # waypoint x relative to the ship
        self.wy = 1  # waypoint y relative to the ship

    def execute(self, i: Instruction):
        if i.type == "N":
            self.wy += i.value
        elif i.type == "S":
            self.wy -= i.value
        elif i.type == "E":
            self.wx += i.value
        elif i.type == "W":
            self.wx -= i.value
        elif i.type == "L":
            self.rotate_waypoint(i.value)
        elif i.type == "R":
            self.rotate_waypoint(-i.value)
        elif i.type == "F":
            self.move_in_waypoint_direction(i.value)

    def rotate_waypoint(self, degrees: float):
        sin = math.sin(math.radians(degrees))
        cos = math.cos(math.radians(degrees))
        x = self.wx
        y = self.wy
        self.wx = x * cos - y * sin
        self.wy = x * sin + y * cos

    def move_in_waypoint_direction(self, value: float):
        self.x += self.wx * value
        self.y += self.wy * value

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
