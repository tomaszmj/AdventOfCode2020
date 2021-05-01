from __future__ import annotations

from typing import List, Callable


class Expression:
    OPERAND = "operand"
    OPERATOR = "operator"

    @classmethod
    def new_operand(cls, value: int):
        return cls(cls.OPERAND, value)

    @classmethod
    def new_operator(cls, value: Operator):
        if not value.is_executable():
            raise ValueError(f"cannot create Expression from operator {value} - is not executable")
        return cls(cls.OPERATOR, value)

    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    @classmethod
    def execute_rpn(cls, rpn: List[Expression]) -> int:
        args = Stack()
        for expression in rpn:
            if expression.kind == cls.OPERAND:
                args.push(expression.value)
            elif expression.kind == cls.OPERATOR:
                expression.value.execute(args)
            else:
                raise ValueError(f"invalid expression kind {expression.kind}")
        retval = args.pop()
        if not args.is_empty():
            raise ValueError(f"invalid RPN expression {rpn}, after executing all operators "
                             f"something remained on stack: {args.values}")
        return retval


class Operator:
    precedence = {
        "*": 1,
        "+": 1,
        "(": 2,
        ")": 2,
    }

    def __init__(self, character: str):
        if character not in "+*()":
            raise ValueError(f"cannot create operator from {character}")
        self.kind = character

    def preceeds(self, other: Operator) -> bool:
        return self.precedence[self.kind] < self.precedence[other.kind]

    def execute(self, operands: Stack):
        if self.kind == "+":
            a = operands.pop()
            b = operands.pop()
            operands.push(a + b)
        elif self.kind == "*":
            a = operands.pop()
            b = operands.pop()
            operands.push(a * b)

    def is_opening_parenthesis(self) -> bool:
        return self.kind == "("

    def is_closing_parenthesis(self) -> bool:
        return self.kind == ")"

    def is_executable(self) -> bool:
        return self.kind in "+*"

    def __str__(self):
        return self.kind

    def __repr__(self):
        return self.kind


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

    def parse(self, line: str) -> List[Expression]:
        self._operator_stack = Stack()
        self._output_queue = []
        self._remaining_text = line
        try:
            while self._remaining_text:
                # print(f"output queue: {self._output_queue}, operator stack {self._operator_stack.values}")
                if not any(action() for action in self._all_actions()):
                    raise RuntimeError(f"none of parser actions was possible, failed to parse: {self._remaining_text}")
            while not self._operator_stack.is_empty():
                self._output_queue.append(Expression.new_operator(self._operator_stack.pop()))
        except ValueError as e:
            raise RuntimeError(f"{e} - probably due to parentheses mismatch in line: {line.strip()}")
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
        self._output_queue.append(Expression.new_operand(number))
        self._remaining_text = self._remaining_text[i:]
        return True

    def _parse_operator(self) -> bool:
        if not self._remaining_text[0] in "+*()":
            return False
        operator = Operator(self._remaining_text[0])
        if operator.is_opening_parenthesis():
            self._operator_stack.push(Operator("("))
        elif operator.is_closing_parenthesis():
            self._handle_closing_bracket()
        else:
            self._handle_non_bracket_operator(operator)
        self._remaining_text = self._remaining_text[1:]
        return True

    def _handle_non_bracket_operator(self, operator: Operator):
        while True:
            if self._operator_stack.is_empty():
                self._operator_stack.push(operator)
                return
            if operator.preceeds(self._operator_stack.peek()):
                self._operator_stack.push(operator)
                return
            else:
                self._output_queue.append(Expression.new_operator(self._operator_stack.pop()))

    def _handle_closing_bracket(self):
        operators_in_bracket = 0
        while True:
            if self._operator_stack.is_empty():
                raise RuntimeError(f"parentheses mismatch, cannot parse {self._remaining_text}")
            operator = self._operator_stack.pop()
            if operator.is_opening_parenthesis():
                if operators_in_bracket == 0:
                    raise RuntimeError(f"no operators inside bracket, cannot parse {self._remaining_text}")
                return
            self._output_queue.append(Expression.new_operator(operator))
            operators_in_bracket += 1

    def _all_actions(self) -> List[Callable]:
        return [self._parse_digit, self._ignore_whitespace, self._parse_operator]


def main():
    parser = RPNParser()
    total = 0
    with open("data.txt") as f:
        for line in f:
            # print(line.rstrip(), "-> ", end="")
            rpn = parser.parse(line)
            # print(" ".join(str(symbol) for symbol in rpn), "-> ", end="")
            result = Expression.execute_rpn(rpn)
            # print(result)
            total += result
    print(f"total: {total}")


if __name__ == "__main__":
    main()
