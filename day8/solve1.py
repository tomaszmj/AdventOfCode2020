from typing import List, Set


class Instruction:
    def __init__(self, input_line: str):
        try:
            self.code = input_line[:3]
            if self.code not in ["nop", "acc", "jmp"]:
                raise ValueError()
            if input_line[4] == "+":
                self.value = int(input_line[5:])
            elif input_line[4] == "-":
                self.value = -int(input_line[5:])
            else:
                raise ValueError()
        except Exception:
            raise ValueError(f'cannot construct instruction from text "{input_line}"')


class Program:
    def __init__(self):
        self.instructions: List[Instruction] = []
    
    def add_instruction(self, instruction: Instruction):
        self.instructions.append(instruction)

    def execute(self) -> int:
        accumulator = 0
        i = 0
        executed_instructions: Set[int] = set()
        while i not in executed_instructions and 0 <= i < len(self.instructions):
            instr = self.instructions[i]
            executed_instructions.add(i)
            if instr.code == "nop":
                i += 1
            elif instr.code == "acc":
                accumulator += instr.value
                i += 1
            elif instr.code == "jmp":
                i += instr.value
        return accumulator


def main():
    program = Program()
    with open("data.txt") as f:
        for line in f:
            program.add_instruction(Instruction(line.strip()))
    print(f"accumulator after executing program: {program.execute()}")


if __name__ == "__main__":
    main()
