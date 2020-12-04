REQUIRED_KEYS = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]


def year_validation_func(min: int, max: int) -> callable:
    def is_year_valid(year: str) -> bool:
        if len(year) != 4:
            return False
        try:
            year_int = int(year)
            if min <= year_int <= max:
                return True
            return False
        except ValueError:
            return False
    return is_year_valid


def height_validation_func(hgt: str) -> bool:
    try:
        num = int(hgt[:-2])
    except ValueError:
        return False
    measure = hgt[-2:]
    if measure == "cm":
        return 150 <= num <= 193
    elif measure == "in":
        return 59 <= num <= 76
    return False


def hair_color_validation_func(hcl: str) -> bool:
    if len(hcl) != 7:
        return False
    if hcl[0] != "#":
        return False
    for c in hcl[1:]:
        if c not in "abcdef0123456789":
            return False
    return True


def password_id_validation_func(pid: str) -> bool:
    if len(pid) != 9:
        return False
    for c in pid:
        if c not in "0123456789":
            return False
    return True


VALIDATION_FUNCTIONS = {
    "byr": year_validation_func(1920, 2002),
    "iyr": year_validation_func(2010, 2020),
    "eyr": year_validation_func(2020, 2030),
    "hgt": height_validation_func,
    "hcl": hair_color_validation_func,
    "ecl": lambda hcl: hcl in {"amb", "blu", "brn", "gry", "grn", "hzl", "oth"},
    "pid": password_id_validation_func,
}


def is_valid(passport: dict) -> bool:
    for key in REQUIRED_KEYS:
        if key not in passport:
            return False
        if not VALIDATION_FUNCTIONS[key](passport[key]):
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
