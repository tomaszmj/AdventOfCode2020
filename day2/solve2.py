if __name__ == "__main__":
    valid_count = 0
    with open("data.txt") as f:
        for line in f:
            split_line = line.split(" ")
            i1 = int(split_line[0].split("-")[0]) - 1
            i2 = int(split_line[0].split("-")[1]) - 1
            checked_char = split_line[1][0]
            text = split_line[2]
            count = 0
            if i1 < len(text):
                if text[i1] == checked_char:
                    count += 1
            if i2 < len(text):
                if text[i2] == checked_char:
                    count += 1
            if count == 1:
                valid_count += 1
    print(valid_count)
