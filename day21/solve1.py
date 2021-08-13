from __future__ import annotations

from typing import Set, Dict, NamedTuple, List
from collections import defaultdict
import time


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
        self.possible_allergens_set_per_ingredient: Dict[str, Set[str]] = defaultdict(set)  # const after all add_entry calls
        self.possible_ingredients_set_per_allergen: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self._all_ingredients_set: Set[str] = set()  # const after all add_entry calls
        self._all_ingredients_matching_any_allergen: Set[str] = set()  # const after _initialize_internals
        self._entries_per_ingredient: Dict[str, List[int]] = defaultdict(list)  # const after all add_entry calls
        self._choices: List[IngredientPerAllergenEntry] = []  # const after _initialize_internals
        self._allergen_per_ingredient: Dict[str, str] = {}  # variable used in _solve
        self._ingredient_per_allergen: Dict[str, str] = {}  # variable used in _solve
        self._failed_solves = 0  # used only for _time_metric
        self._t = time.time()  # used only for _time_metric

    def add_entry(self, entry: FoodEntry):
        self.entries.append(entry)
        self._all_ingredients_set.update(entry.ingredients)
        for ingredient in entry.ingredients:
            self._entries_per_ingredient[ingredient].append(len(self.entries) - 1)
            self.possible_allergens_set_per_ingredient[ingredient].update(entry.allergens)
        for allergen in entry.allergens:
            if allergen in self.possible_ingredients_set_per_allergen:
                self.possible_ingredients_set_per_allergen[allergen].intersection_update(set(entry.ingredients))
            else:
                self.possible_ingredients_set_per_allergen[allergen] = set(entry.ingredients)

    def validate(self) -> bool:
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

    def partial_validate(self, entry_index: int) -> bool:
        entry = self.entries[entry_index]
        allergens = set()
        for ingredient in entry.ingredients:
            allergen = self._allergen_per_ingredient.get(ingredient, "")
            if not allergen:
                continue
            if allergen in allergens:
                return False  # allergens cannot repeat
            allergens.add(allergen)
        missing_allergens = 0
        for expected_allergen in entry.allergens:
            if expected_allergen not in allergens:
                missing_allergens += 1
        max_missing_allergens = len(entry.ingredients) - len(allergens)
        retval = bool(missing_allergens <= max_missing_allergens)
        # print(f"partial_validate: {retval}")
        return retval

    def solve(self):
        self._initialize_internals()
        print(self.possible_choices_to_str())
        print(f"staring solve with {len(self.possible_allergens_set_per_ingredient)} ingredients and "
              f"{len(self.possible_ingredients_set_per_allergen)} allergens, choices:\n"
              f"{self.possible_ingredients_per_allergen_to_str()}")
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

    def possible_ingredients_per_allergen_to_str(self) -> str:
        return "\n".join(
            (f"{choice.allergen}: {len(choice.possible_ingredients)}" for choice in self._choices)
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
        self._time_metric()
        if len(self._ingredient_per_allergen) == len(self._choices):
            return self.validate()
        entry = self._choices[len(self._ingredient_per_allergen)]
        for ingredient in entry.possible_ingredients:
            if ingredient in self._allergen_per_ingredient:
                continue
            self._allergen_per_ingredient[ingredient] = entry.allergen
            self._ingredient_per_allergen[entry.allergen] = ingredient
            if all((self.partial_validate(i) for i in self._entries_per_ingredient[ingredient])):
                if self._solve():
                    return True
            self._failed_solves += 1
            # else - backtrack...
            del self._allergen_per_ingredient[ingredient]
            del self._ingredient_per_allergen[entry.allergen]
        return False

    def _initialize_internals(self):
        self._allergen_per_ingredient: Dict[str, str] = {}
        self._ingredient_per_allergen: Dict[str, str] = {}
        self._choices = []
        for allergen, possible_ingredients in self.possible_ingredients_set_per_allergen.items():
            self._all_ingredients_matching_any_allergen.update(possible_ingredients)
            entry = IngredientPerAllergenEntry(allergen=allergen, possible_ingredients=list(possible_ingredients))
            self._choices.append(entry)
        self._choices.sort(key=lambda c: len(c.possible_ingredients))
        print(f"ingredients matching: {len(self._all_ingredients_matching_any_allergen)} / {len(self._all_ingredients_set)}")
        self._failed_solves = 0
        self._t = time.time()

    def _time_metric(self):
        t = time.time()
        dur = t - self._t
        if dur > 30:
            print(f"failed _solves for last {dur}s: {self._failed_solves}")
            self._failed_solves = 0
            self._t = t


def main():
    data = Data()
    with open("data.txt") as f:
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
