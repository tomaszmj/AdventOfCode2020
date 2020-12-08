def main():
    total = 0
    group_yes_answers = set()
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                total += len(group_yes_answers)
                group_yes_answers = set()
                continue
            for c in line:
                group_yes_answers.add(c)
    total += len(group_yes_answers) # last group (in case there was no empty line at the end)
    print(total)


if __name__ == "__main__":
    main()
