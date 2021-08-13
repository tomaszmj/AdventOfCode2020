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


class IngredientPerAllergenEntry(NamedTuple):
    allergen: str
    possible_ingredients: List[str]


class Data:
    def __init__(self):
        self._entries = []  # const after all add_entry calls
        self._possible_ingredients_set_per_allergen: Dict[str, Set[str]] = {}  # const after all add_entry calls
        self._all_ingredients_set: Set[str] = set()  # const after all add_entry calls
        self._choices: List[IngredientPerAllergenEntry] = []  # const after _initialize_internals
        self._allergen_per_ingredient: Dict[str, str] = {}  # variable used in _solve
        self._ingredient_per_allergen: Dict[str, str] = {}  # variable used in _solve

    def add_entry(self, entry: FoodEntry):
        self._entries.append(entry)
        self._all_ingredients_set.update(entry.ingredients)
        for allergen in entry.allergens:
            if allergen in self._possible_ingredients_set_per_allergen:
                self._possible_ingredients_set_per_allergen[allergen].intersection_update(set(entry.ingredients))
            else:
                self._possible_ingredients_set_per_allergen[allergen] = set(entry.ingredients)

    def solve(self):
        self._initialize_internals()
        print(f"staring solve with {len(self._all_ingredients_set)} ingredients and "
              f"{len(self._possible_ingredients_set_per_allergen)} allergens, choices:\n"
              f"{self.possible_ingredients_per_allergen_to_str()}")
        return self._solve()

    def possible_ingredients_per_allergen_to_str(self) -> str:
        return "\n".join(
            f"{choice.allergen}: {choice.possible_ingredients} (total {len(choice.possible_ingredients)})"
            for choice in self._choices
        )

    def chosen_ingredient_per_allergen_to_str(self) -> str:
        allergens = (choice.allergen for choice in self._choices)
        return "\n".join(
            (f"{allergen}: {self._ingredient_per_allergen.get(allergen, '')}" for allergen in allergens)
        )

    def canonical_dangerous_ingredients(self) -> str:
        data = list((allergen, ingredient) for allergen, ingredient in self._ingredient_per_allergen.items())
        data.sort(key=lambda d: d[0])  # sort by allergen
        return ",".join(d[1] for d in data)  # return dangerous ingredients list sorted by allergen

    def _solve(self) -> bool:
        if len(self._ingredient_per_allergen) == len(self._choices):
            is_valid = self._validate()
            print(f"iteration of backtracking finished, validation: {is_valid}")
            return is_valid
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

    # In my first solution version _validate was crucial for backtracking.
    # Then, with intersection of _possible_ingredients_set_per_allergen,
    # it turned of that it is not really needed, i.e. the first finished iteration of
    # backtracking finds the correct solution. I am leaving it here just as a sanity check.
    def _validate(self) -> bool:
        for i, entry in enumerate(self._entries):
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

    def _initialize_internals(self):
        self._allergen_per_ingredient: Dict[str, str] = {}
        self._ingredient_per_allergen: Dict[str, str] = {}
        self._choices = []
        for allergen, possible_ingredients in self._possible_ingredients_set_per_allergen.items():
            entry = IngredientPerAllergenEntry(allergen=allergen, possible_ingredients=list(possible_ingredients))
            self._choices.append(entry)
        self._choices.sort(key=lambda c: len(c.possible_ingredients))


def main():
    data = Data()
    with open("data.txt") as f:
        for i, line in enumerate(f):
            entry = FoodEntry.from_string(line.strip())
            data.add_entry(entry)
    if data.solve():
        canonical_dangerous_ingredients = data.canonical_dangerous_ingredients()
        print(f"solve ok:\n{data.chosen_ingredient_per_allergen_to_str()}\nanswer: {canonical_dangerous_ingredients}")
    else:
        print("solve failed")


if __name__ == "__main__":
    main()
