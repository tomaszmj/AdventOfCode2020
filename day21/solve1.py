from __future__ import annotations

from typing import Set, Dict, NamedTuple, List, Iterable
import itertools


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


class IngredientEntry(NamedTuple):
    ingredient: str
    possible_allergens: List[str]


class Data:
    def __init__(self):
        self.entries = []  # const after all add_entry calls
        self.possible_allergens_set_per_ingredient: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self._all_allergens_set: Set[str] = set()  # const after all add_entry calls
        self._all_allergens_list: List[str] = []  # const after _initialize_internals
        self._choices: List[IngredientEntry] = []  # const after _initialize_internals
        self._allergen_per_ingredient: Dict[str, str] = {}  # variable used in _solve
        # self._all_chosen_allergens: Set[str] = set()  # variable used in _solve
        # self._current_choice_state: List[int] = []  # variable used in _solve

    def add_entry(self, entry: FoodEntry):
        self.entries.append(entry)
        for ingredient in entry.ingredients:
            if ingredient not in self.possible_allergens_set_per_ingredient:
                self.possible_allergens_set_per_ingredient[ingredient] = set()
            self.possible_allergens_set_per_ingredient[ingredient].update(entry.allergens)
        self._all_allergens_set.update(entry.allergens)

    def validate_chosen_allergens(self) -> bool:
        for i, entry in enumerate(self.entries):
            allergens = set()
            for ingredient in entry.ingredients:
                allergen = self._allergen_per_ingredient.get(ingredient, "")
                if not allergen:
                    continue
                if allergen in allergens:
                    return False  # allergens cannot repeat
                allergens.add(allergen)
            for expected_allergen in entry.allergens:
                if expected_allergen not in allergens:
                    return False
        return True

    def solve(self):
        self._initialize_internals()
        print(f"staring solve with {len(self._choices)} ingredients and {len(self._all_allergens_set)} allergens, "
              f"possible choices:\n{self.possible_choices_to_str()}")
        return self._solve()

    def possible_choices_to_str(self) -> str:
        return "\n".join(
            f"{choice.ingredient}: {choice.possible_allergens}"
            for choice in self._choices
        )

    def chosen_allergens_to_str(self) -> str:
        ingredients = (choice.ingredient for choice in self._choices)
        return "\n".join(
            (f"{ingredient}: {self._allergen_per_ingredient.get(ingredient, '')}" for ingredient in ingredients)
        )

    def magic_number(self) -> int:
        ingredients_without_allergens = set()
        for ingredient in (choice.ingredient for choice in self._choices):
            if not self._allergen_per_ingredient.get(ingredient, ""):
                ingredients_without_allergens.add(ingredient)
        result = 0
        for entry in self.entries:
            for ingredient in entry.ingredients:
                if ingredient in ingredients_without_allergens:
                    result += 1
        return result

    def _solve(self) -> bool:
        for ingredients_with_allergens in itertools.combinations(self._choices, len(self._all_allergens_set)):
            for allergens_order in itertools.permutations(self._all_allergens_list, len(self._all_allergens_list)):
                if not self._brutal_allergens_choice(allergens_order, ingredients_with_allergens):
                    continue
                if self.validate_chosen_allergens():
                    return True
        return False

    def _brutal_allergens_choice(self, allergens: Iterable[str], ingredients_chosen: Iterable[IngredientEntry]) -> bool:
        self._allergen_per_ingredient.clear()
        for allergen, choice in zip(allergens, ingredients_chosen):
            if allergen not in choice.possible_allergens:
                return False
            self._allergen_per_ingredient[choice.ingredient] = allergen
        return True

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
    # def _next_choice(self) -> bool:
    #     for i, choice in enumerate(self._choices):
    #         last_allergen_index = self._current_choice_state[i]
    #         new_allergen_index = last_allergen_index + 1
    #         if new_allergen_index == len(choice.possible_allergens):
    #             new_allergen_index = -1
    #         self._current_choice_state[i] = new_allergen_index
    #         if new_allergen_index < 0:  # reset allergen selection
    #             del self._allergen_per_ingredient[choice.ingredient]
    #         else:
    #             new_allergen = choice.possible_allergens[new_allergen_index]
    #             self._allergen_per_ingredient[choice.ingredient] = new_allergen
    #             return True
    #     return False

    def _initialize_internals(self):
        self._all_allergens_list = list(self._all_allergens_set)
        # self._all_chosen_allergens = set()
        self._allergen_per_ingredient = {}
        self._choices = []
        for ingredient, possible_allergens in self.possible_allergens_set_per_ingredient.items():
            allergens_list = list(possible_allergens)
            self._choices.append(IngredientEntry(ingredient=ingredient, possible_allergens=allergens_list))
        # self._current_choice_state = [-1] * len(self._choices)


def main():
    data = Data()
    with open("data_small.txt") as f:
        for i, line in enumerate(f):
            entry = FoodEntry.from_string(line.strip())
            data.add_entry(entry)
    if data.solve():
        magic_number = data.magic_number()
        print(f"solve ok:\n{data.chosen_allergens_to_str()}\nanswer: {magic_number}")
    else:
        print("solve failed")


if __name__ == "__main__":
    main()
