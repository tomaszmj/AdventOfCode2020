REQUIRED_KEYS = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]


def is_valid(passport: dict) -> bool:
    for key in REQUIRED_KEYS:
        if key not in passport:
            return False
    if len(passport) == len(REQUIRED_KEYS):
        return True
    if len(passport) == len(REQUIRED_KEYS) + 1 and "cid" in passport:
        return True
    return False


def main():
    valid_passports = 0
    current_passport = {}
    with open("data.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                if is_valid(current_passport):
                    valid_passports += 1
                current_passport = {}
            else:
                fields = line.split(" ")
                for field in fields:
                    key = field.split(":")[0]
                    value = field.split(":")[1]
                    current_passport[key] = value
    print(f"valid passports: {valid_passports}")


if __name__ == "__main__":
    main()
