def main():
    max_id = -1
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if len(line) != 10:
                raise ValueError(f"unexpected line {line} in input file")
            max_id = max(max_id, int("".join("1" if c in "BR" else "0" for c in line), 2))
    print(f"Heighest seat ID: {max_id}")

if __name__ == "__main__":
    main()
