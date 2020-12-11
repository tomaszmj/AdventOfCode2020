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

    # returns (accumulator, did program try to loop)
    def execute(self) -> (int, bool):
        accumulator = 0
        i = 0
        executed_instructions: Set[int] = set()
        while i not in executed_instructions:
            if i >= len(self.instructions) or i < 0:
                return accumulator, False
            instr = self.instructions[i]
            executed_instructions.add(i)
            if instr.code == "nop":
                i += 1
            elif instr.code == "acc":
                accumulator += instr.value
                i += 1
            elif instr.code == "jmp":
                i += instr.value
        return accumulator, True

    def modify_and_execute_until_there_is_no_loop(self) -> int:
        for i, instr in enumerate(self.instructions):
            code = instr.code
            if code == "nop":
                self.instructions[i].code = "jmp"
            elif code == "jmp":
                self.instructions[i].code = "nop"
            elif code == "acc":
                continue
            accumulator, looped = self.execute()
            if not looped:
                return accumulator
            self.instructions[i].code = code
        raise RuntimeError("program looped for all possible instruction modifications")
             


def main():
    program = Program()
    with open("data.txt") as f:
        for line in f:
            program.add_instruction(Instruction(line.strip()))
    print(f"accumulator after fixing and executing program: {program.modify_and_execute_until_there_is_no_loop()}")


if __name__ == "__main__":
    main()
