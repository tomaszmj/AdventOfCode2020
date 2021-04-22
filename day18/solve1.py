from __future__ import annotations

from typing import List, Callable


# class Lexeme:
#     def __init__(self, characters: str):
#         pass
#
#     def kind(self):
#         return "operand"


class Operator:
    precedence = {
        "*": 0,  # temporary for tests
        "+": 1,
        "(": 2,
        ")": 2,
    }

    def __init__(self, character: str):
        if character not in "+*()":
            raise ValueError(f"cannot create operator from {character}")
        self.type = character

    def preceeds(self, other: Operator) -> bool:
        return self.precedence[self.type] < self.precedence[other.type]

    def execute(self, operands: Stack):
        if self.type == "+":
            a = operands.pop()
            b = operands.pop()
            operands.push(a + b)
        elif self.type == "*":
            a = operands.pop()
            b = operands.pop()
            operands.push(a * b)

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.type


class Stack:
    def __init__(self):
        self.values = []

    def push(self, value):
        self.values.append(value)

    def pop(self):
        return self.values.pop()

    def peek(self):
        return self.values[-1]

    def is_empty(self):
        return len(self.values) == 0


class RPNParser:
    def __init__(self):
        self._operator_stack = Stack()
        self._output_queue = []
        self._remaining_text = ""

    def parse(self, line: str) -> List[Lexeme]:
        self._operator_stack = Stack()
        self._output_queue = []
        self._remaining_text = line
        while self._remaining_text:
            print(f"output queue: {self._output_queue}, operator stack {self._operator_stack.values}")
            if not any(action() for action in self._all_actions()):
                raise RuntimeError(f"none of parser actions was possible, failed to parse: {self._remaining_text}")
        while not self._operator_stack.is_empty():
            self._output_queue.append(self._operator_stack.pop())
        return self._output_queue

    def _ignore_whitespace(self) -> bool:
        if not self._remaining_text[0] in " \n":
            return False
        self._remaining_text = self._remaining_text[1:]
        return True

    def _parse_digit(self) -> bool:
        if not self._remaining_text[0].isdigit():
            return False
        i = 0
        while self._remaining_text[i].isdigit():
            i += 1
        number = int(self._remaining_text[0:i])
        self._output_queue.append(number)
        self._remaining_text = self._remaining_text[i:]
        return True

    def _parse_operator(self) -> bool:
        # TODO handle parentheses
        if not self._remaining_text[0] in "+*()":
            return False
        operator = Operator(self._remaining_text[0])
        self._remaining_text = self._remaining_text[1:]
        while True:
            if self._operator_stack.is_empty():
                self._operator_stack.push(operator)
                break
            if operator.preceeds(self._operator_stack.peek()):
                self._operator_stack.push(operator)
                break
            else:
                self._output_queue.append(self._operator_stack.pop())
        return True

    def _all_actions(self) -> List[Callable]:
        return [self._parse_digit, self._ignore_whitespace, self._parse_operator]


def main():
    parser = RPNParser()
    with open("data_small.txt") as f:
        for line in f:
            rpn = parser.parse(line)
            print(" ".join(str(symbol) for symbol in rpn))


if __name__ == "__main__":
    main()
