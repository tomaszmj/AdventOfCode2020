from __future__ import annotations

from typing import List, Dict, Set, NamedTuple


class Rule:
    def __init__(self, text: str):
        parts = text.split(":")
        if len(parts) != 2:
            raise ValueError(f"cannot create Rule, syntax error (expected <index>: <description>) in {text}")
        self.index = int(parts[0])
        description = parts[1]
        self.literal: str = ""
        self.child_rules: List[List[int]] = []
        if '"' in description:
            self._parse_literal(description)
        else:
            self._parse_child_rules(description)

    def _parse_child_rules(self, description: str):
        alternatives = description.split("|")
        for alternative in alternatives:
            rule_chain = []
            for rule_str in alternative.split(" "):
                rule_str = rule_str.replace(" ", "")
                if rule_str:
                    rule_chain.append(int(rule_str))
            if len(rule_chain) == 0:
                raise ValueError(f"cannot parse, one of alternatives in rule is empty: {description}")
            self.child_rules.append(rule_chain)

    def _parse_literal(self, description: str):
        quote_begin = description.find('"')
        quote_end = description.find('"', quote_begin+1)
        self.literal = description[quote_begin+1:quote_end]

    # for parsing tests only
    def __str__(self):
        if self.literal:
            return f'{self.index}: "{self.literal}"'
        return f'{self.index}: {" | ".join(str(chain) for chain in self.child_rules)}'


class BacktrackingEntryKey(NamedTuple):
    rulenum: int
    text_to_parse: str


class Backtracker:
    def __init__(self):
        self.choices: Dict[BacktrackingEntryKey, Set[int]] = {}
        self.used_choices: Dict[BacktrackingEntryKey, Set[int]] = {}

    def add_choice_if_not_used(self, entry: BacktrackingEntryKey, child_index: int):
        if entry in self.used_choices:
            if child_index in self.used_choices[entry]:
                return
        if entry not in self.choices:
            self.choices[entry] = {child_index}
        else:
            self.choices[entry].add(child_index)

    def has_choices(self, entry: BacktrackingEntryKey) -> bool:
        return entry in self.choices

    def has_any_choice(self):
        return len(self.choices) > 0

    def use_some_choice(self, entry: BacktrackingEntryKey) -> int:
        l = len(self.choices[entry])
        index = self.choices[entry].pop()
        print(f"use_some_choice({entry}) returning {index}, out of {l} choices")
        if len(self.choices[entry]) == 0:
            del(self.choices[entry])
        if entry not in self.used_choices:
            self.used_choices[entry] = {index}
        else:
            self.used_choices[entry].add(index)
        return index


class Parser:
    def __init__(self):
        self.rules: Dict[int, Rule] = {}

    def add_rule(self, rule: Rule):
        if rule.index in self.rules:
            raise ValueError(f"cannot add rule {rule.index} twice")
        self.rules[rule.index] = rule

    def match(self, text: str) -> bool:
        return self._backtracked_match(0, text)

    def _backtracked_match(self, rulenum: int, text: str) -> bool:
        backtracker = Backtracker()
        ok, remaining_text = self._match(rulenum, text, backtracker)
        if ok and len(remaining_text) == 0:
            return True
        while backtracker.has_any_choice():
            input()
            ok, remaining_text = self._match(rulenum, text, backtracker)
            if ok and len(remaining_text) == 0:
                return True
        return False

    # if text matches given parser rule, returns True and remaining text (used in subsequent _match calls)
    def _match(self, rulenum: int, text: str, backtracker: Backtracker) -> (bool, str):
        backtracker_key = BacktrackingEntryKey(rulenum, text)
        print(f"_match({rulenum}, {text}, backtracking choices len: {len(backtracker.choices)})")
        rule = self.rules[rulenum]
        # if rule is literal, return immediately without recursion
        if rule.literal:
            if text.startswith(rule.literal):
                return True, text[len(rule.literal):]
            else:
                return False, text
        # else, for each alternative rule chain check if it matches recursively
        # some matches have already been checked in previous calls, so they will be rejected by backtracker
        for i, _ in enumerate(rule.child_rules):
            backtracker.add_choice_if_not_used(backtracker_key, i)
        while backtracker.has_choices(backtracker_key):
            child_chain_index = backtracker.use_some_choice(backtracker_key)
            ok, remaining_text = self._match_rule_chain(rule.child_rules[child_chain_index], text, backtracker)
            if ok:
                return True, remaining_text
        return False, text

    # check if text matches all rules specified in the chain (concatenated one after another)
    def _match_rule_chain(self, rulenums: List[int], text, backtracker: Backtracker) -> (bool, str):
        remaining_text = text
        for num in rulenums:
            ok, remaining_text = self._match(num, remaining_text, backtracker)
            if ok:
                text = remaining_text
            else:
                return False, text
        return True, remaining_text

    # def generate_possible_matches(self, rulenum: int) -> List[str]:
    #     return self._generate_possible_matches(rulenum, "", set())
    #
    # def _generate_possible_matches(self, rulenum: int, got_text: str, open_calls: Set[int]) -> List[str]:
    #     if rulenum in open_calls:
    #         raise RuntimeError(f"infinite recursion detected when generation possible matches for rule {rulenum}")
    #     open_calls.add(rulenum)
    #     rule = self.rules[rulenum]
    #     if rule.literal:
    #         open_calls.remove(rulenum)
    #         return [got_text + rule.literal]
    #     possible_evaluations = []
    #     for alternative in rule.child_rules:
    #         current_text = got_text
    #         for chain_rule_num in alternative:
    #             possibilities = self._generate_possible_matches(chain_rule_num, current_text, open_calls)
                # chain_element_evaluation = current_text + possibility

    # def _generate_chain_possible_matches(self, rulenum: int, got_text: str, open_calls: Set[int]) -> List[str]:


def main():
    parser = Parser()
    matches = 0
    with open("data_small2.txt") as f:
        line = f.readline().strip()
        while line:
            rule = Rule(line)
            if rule.index == 8:
                rule = Rule("8: 42 | 42 8")
            elif rule.index == 11:
                rule = Rule("11: 42 31 | 42 11 31")
            # print(rule)
            parser.add_rule(rule)
            line = f.readline().strip()
        line = f.readline().strip()
        while line:
            print(f"{line} -> ", end="")
            if parser.match(line):
                matches += 1
                print("ok")
            else:
                print("no")
            line = f.readline().strip()
    print(f"matches: {matches}")


if __name__ == "__main__":
    main()
