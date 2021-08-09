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


class AllergenPerIngredientEntry(NamedTuple):
    ingredient: str
    possible_allergens: List[str]


class IngredientPerAllergenEntry(NamedTuple):
    allergen: str
    possible_ingredients: List[str]


class Data:
    def __init__(self):
        self.entries = []  # const after all add_entry calls
        self.possible_allergens_set_per_ingredient: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self.possible_ingredients_set_per_allergen: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self._all_ingredients_set: Set[str] = set()  # const after all add_entry calls
        self._choices: List[IngredientPerAllergenEntry] = []  # const after _initialize_internals
        self._allergen_per_ingredient: Dict[str, str] = {}  # variable used in _solve
        self._ingredient_per_allergen: Dict[str, str] = {}  # variable used in _solve

    def add_entry(self, entry: FoodEntry):
        self.entries.append(entry)
        self._all_ingredients_set.update(entry.ingredients)
        for ingredient in entry.ingredients:
            if ingredient not in self.possible_allergens_set_per_ingredient:
                self.possible_allergens_set_per_ingredient[ingredient] = set()
            self.possible_allergens_set_per_ingredient[ingredient].update(entry.allergens)
        for allergen in entry.allergens:
            if allergen not in self.possible_ingredients_set_per_allergen:
                self.possible_ingredients_set_per_allergen[allergen] = set()
            self.possible_ingredients_set_per_allergen[allergen].update(entry.ingredients)

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
        print(f"staring solve with {len(self.possible_allergens_set_per_ingredient)} ingredients and "
              f"{len(self.possible_ingredients_set_per_allergen)} allergens")
        return self._solve()

    def possible_choices_to_str(self) -> str:
        return "\n".join(
            f"{choice.allergen}: {choice.possible_ingredients}"
            for choice in self._choices
        )

    def chosen_allergen_per_ingredient_to_str(self) -> str:
        ingredients = self._all_ingredients_set
        return "\n".join(
            (f"{ingredient}: {self._allergen_per_ingredient.get(ingredient, '')}" for ingredient in ingredients)
        )

    def chosen_ingredient_per_allergen_to_str(self) -> str:
        allergens = (choice.allergen for choice in self._choices)
        return "\n".join(
            (f"{allergen}: {self._ingredient_per_allergen.get(allergen, '')}" for allergen in allergens)
        )

    def ingredients_without_allergens(self) -> Set[str]:
        ingredients_without_allergens = set()
        for ingredient in self._all_ingredients_set:
            if not self._allergen_per_ingredient.get(ingredient, ""):
                ingredients_without_allergens.add(ingredient)
        return ingredients_without_allergens

    def magic_number(self) -> int:
        ingredients_without_allergens = self.ingredients_without_allergens()
        result = 0
        for entry in self.entries:
            for ingredient in entry.ingredients:
                if ingredient in ingredients_without_allergens:
                    result += 1
        return result

    def _solve(self) -> bool:
        if len(self._ingredient_per_allergen) == len(self._choices):
            return self.validate_chosen_allergens()
        entry = self._choices[len(self._ingredient_per_allergen)]
        for ingredient in entry.possible_ingredients:
            if ingredient in self._allergen_per_ingredient:
                continue
            self._allergen_per_ingredient[ingredient] = entry.allergen
            self._ingredient_per_allergen[entry.allergen] = ingredient
            if self._solve():
                return True
            # else - backtrack...
            del self._allergen_per_ingredient[ingredient]
            del self._ingredient_per_allergen[entry.allergen]
        return False

    def _initialize_internals(self):
        self._allergen_per_ingredient: Dict[str, str] = {}
        self._ingredient_per_allergen: Dict[str, str] = {}
        self._choices = []
        for allergen, possible_ingredients in self.possible_ingredients_set_per_allergen.items():
            entry = IngredientPerAllergenEntry(allergen=allergen, possible_ingredients=list(possible_ingredients))
            self._choices.append(entry)


def main():
    data = Data()
    with open("data_small.txt") as f:
        for i, line in enumerate(f):
            entry = FoodEntry.from_string(line.strip())
            data.add_entry(entry)
    if data.solve():
        magic_number = data.magic_number()
        print(f"solve ok:\n{data.chosen_ingredient_per_allergen_to_str()}\nanswer: {magic_number}")
    else:
        print("solve failed")


if __name__ == "__main__":
    main()
