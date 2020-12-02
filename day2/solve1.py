if __name__ == "__main__":
    valid_count = 0
    with open("data.txt") as f:
        for line in f:
            split_line = line.split(" ")
            lower_count = int(split_line[0].split("-")[0])
            upper_count = int(split_line[0].split("-")[1])
            checked_char = split_line[1][0]
            text = split_line[2]
            count = 0
            for c in text:
                if c == checked_char:
                    count += 1
            if count <= upper_count and count >= lower_count:
                valid_count += 1
    print(valid_count)
