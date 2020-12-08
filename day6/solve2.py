def count_values(values, expected_value) -> int:
    total = 0
    for v in values:
        if v == expected_value:
            total += 1
    return total


def main():
    total = 0
    group_yes_answers, group_count = {}, 0
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                total += count_values(group_yes_answers.values(), group_count)
                group_yes_answers, group_count = {}, 0
                continue
            group_count += 1
            for c in line:
                if c in group_yes_answers:
                    group_yes_answers[c] += 1
                else:
                    group_yes_answers[c] = 1
    total += count_values(group_yes_answers.values(), group_count)
    print(total)


if __name__ == "__main__":
    main()
