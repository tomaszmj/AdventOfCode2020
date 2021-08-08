from __future__ import annotations

from typing import Set, Dict, NamedTuple, List


class FoodEntry(NamedTuple):
    ingredients: List[str]
    allergens: List[str]

    @classmethod
    def from_string(cls, line: str):
        allergens_index = line.find(" (")
        ingredients_list = line[:allergens_index].split(" ")
        allergens_list_str = line[allergens_index:]
        if not allergens_list_str.startswith(" (contains ") or not allergens_list_str.endswith(")"):
            raise ValueError(f"invalid allergens list on line: {line}")
        allergens_list = allergens_list_str[len("(contains "):-1].replace(" ", "").split(",")
        ingredients_list.sort()
        allergens_list.sort()
        return FoodEntry(ingredients=ingredients_list, allergens=allergens_list)


class AllergenChoiceEntry(NamedTuple):
    ingredient: str
    possible_allergens: List[str]


class Data:
    def __init__(self):
        self.entries = []  # const after all add_entry calls
        self.possible_allergens_set_per_ingredient: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self._all_allergens: Set[str] = set()  # const after _initialize_internals
        self._choices: List[AllergenChoiceEntry] = []  # const after _initialize_internals
        self._chosen_allergens_per_ingredient: Dict[str, str] = {}  # variable used in _solve
        self._all_chosen_allergens: Set[str] = set()  # variable used in _solve
        self._current_choice_state: List[int] = []  # variable used in _solve

    def add_entry(self, entry: FoodEntry):
        self.entries.append(entry)
        for ingredient in entry.ingredients:
            if ingredient not in self.possible_allergens_set_per_ingredient:
                self.possible_allergens_set_per_ingredient[ingredient] = set()
            self.possible_allergens_set_per_ingredient[ingredient].update(entry.allergens)
        self._all_allergens.update(entry.allergens)

    def validate_chosen_allergens(self) -> bool:
        for i, entry in enumerate(self.entries):
            allergens = []
            for ingredient in entry.ingredients:
                allergen = self._chosen_allergens_per_ingredient[ingredient]
                if allergen:
                    allergens.append(allergen)
            allergens.sort()
            if allergens != entry.allergens:  # entry.allergens are already sorted
                # print(f"validate_chosen_allergens failed at entry {i}:\n"
                #       f"got {allergens}, want {entry.allergens}\n"
                #       f"{self.chosen_allergens_to_str()}")
                return False
        print(f"validate_chosen_allergens OK:\n{self.chosen_allergens_to_str()}")
        return True

    def solve(self):
        self._initialize_internals()
        print(f"staring solve with possible choices:\n{self.possible_choices_to_str()}")
        if self._solve():
            print(f"solve ok:\n{self.chosen_allergens_to_str()}")
        else:
            print("solve failed")

    def possible_choices_to_str(self) -> str:
        return "\n".join(
            f"{choice.ingredient}: {choice.possible_allergens}"
            for choice in self._choices
        )

    def chosen_allergens_to_str(self) -> str:
        ingredients = (choice.ingredient for choice in self._choices)
        return "\n".join(
            (f"{ingredient}: {self._chosen_allergens_per_ingredient[ingredient]}" for ingredient in ingredients)
        )

    def _solve(self) -> bool:
        while self._next_choice():
            if self.validate_chosen_allergens():
                return True
        return False

    # _next_choice selects allergens per ingredient in a way similar to "written addition" algorithm.
    # Imagine each element of self._current_choice_state being one place in a long number,
    # the number of digits is equal to the number of ingredients,
    # the number of "digits" for each ingredient is number of possible allergens + 1
    # (digit -1 means no allergen selected, other means allergen of given index).
    # Digit number 0 is least significant, number len(self._choices) - 1 is most significant.
    # Function iterates for each ingredient and checks last_allergen_index.
    # If it can be incremented at given position, it is done -> a new ingredient is chosen.
    # If it cannot be incremented (we got to the last position in possible_allergens),
    # we set new_allergen_index = -1 and go to the next position - in "written addition"
    # it is like setting 0 and going to the next position with overflow 1.
    # Function returns False if all positions overflowed, i.e. previous iteration was the last one
    def _next_choice(self) -> bool:
        for i, choice in enumerate(self._choices):
            last_allergen_index = self._current_choice_state[i]
            new_allergen_index = last_allergen_index + 1
            if new_allergen_index == len(choice.possible_allergens):
                new_allergen_index = -1
            self._current_choice_state[i] = new_allergen_index
            if new_allergen_index < 0:  # reset allergen selection
                self._chosen_allergens_per_ingredient[choice.ingredient] = ""
            else:
                new_allergen = choice.possible_allergens[new_allergen_index]
                self._chosen_allergens_per_ingredient[choice.ingredient] = new_allergen
                return True
        return False

    def _initialize_internals(self):
        self._all_chosen_allergens = set()
        self._chosen_allergens_per_ingredient = {}
        for ingredient in self.possible_allergens_set_per_ingredient.keys():
            self._chosen_allergens_per_ingredient[ingredient] = ""
        self._choices = []
        for ingredient, possible_allergens in self.possible_allergens_set_per_ingredient.items():
            allergens_list = list(possible_allergens)
            self._choices.append(AllergenChoiceEntry(ingredient=ingredient, possible_allergens=allergens_list))
        self._current_choice_state = [-1] * len(self._choices)


def main():
    data = Data()
    with open("data_small.txt") as f:
        for i, line in enumerate(f):
            entry = FoodEntry.from_string(line.strip())
            data.add_entry(entry)
    data.solve()


if __name__ == "__main__":
    main()
