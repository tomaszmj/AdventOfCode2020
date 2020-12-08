def main():
    ids = set()
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if len(line) != 10:
                raise ValueError(f"unexpected line {line} in input file")
            ids.add(int("".join("1" if c in "BR" else "0" for c in line), 2))
    for i in range(0, 2**10):
        if i not in ids:
                if i - 1 in ids and i + 1 in ids:
                    print(i)


if __name__ == "__main__":
    main()
