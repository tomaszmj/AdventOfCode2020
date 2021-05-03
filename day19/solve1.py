from __future__ import annotations

from typing import List, Dict


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


class Parser:
    def __init__(self):
        self.rules: Dict[int, Rule] = {}

    def add_rule(self, rule: Rule):
        if rule.index in self.rules:
            raise ValueError(f"cannot add rule {rule.index} twice")
        self.rules[rule.index] = rule

    def match(self, text: str) -> bool:
        ok, remaining_text = self._match(0, text)
        return ok and len(remaining_text) == 0

    # if text matches given parser rule, returns True and remaining text (used in subsequent _match calls)
    def _match(self, rulenum: int, text: str) -> (bool, str):
        rule = self.rules[rulenum]
        # if rule is literal, return immediately without recursion
        if rule.literal:
            if text.startswith(rule.literal):
                return True, text[len(rule.literal):]
            else:
                return False, text
        # else, for each alternative rule chain check if it matches recursively
        for alternative in rule.child_rules:
            ok, remaining_text = self._match_rule_chain(alternative, text)
            if ok:
                return True, remaining_text
        # if we get here, none of the alternatives matched
        return False, text

    # check if text matches all rules specified in the chain (concatenated one after another)
    def _match_rule_chain(self, rulenums: List[int], text) -> (bool, str):
        remaining_text = text
        for num in rulenums:
            ok, remaining_text = self._match(num, remaining_text)
            if ok:
                text = remaining_text
            else:
                return False, text
        return True, remaining_text


def main():
    parser = Parser()
    matches = 0
    with open("data.txt") as f:
        line = f.readline().strip()
        while line:
            rule = Rule(line)
            # print(rule)
            parser.add_rule(rule)
            line = f.readline().strip()
        line = f.readline().strip()
        while line:
            # print(f"{line} -> ", end="")
            if parser.match(line):
                matches += 1
            #     print("ok")
            # else:
            #     print("no")
            line = f.readline().strip()
    print(f"matches: {matches}")


if __name__ == "__main__":
    main()
