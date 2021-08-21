# Puzzle input:
CARD_PUBLIC_KEY = 13316116
DOOR_PUBLIC_KEY = 13651422
PUBLIC_KEY_SUBJECT_NUMBER = 7
DIVISOR = 20201227 


def transform_number(subject_number, loop_size: int) -> int:
    x = 1
    for _ in range(loop_size):
        x = (x * subject_number) % DIVISOR
    return x


def loop_size_of_known_key(key: int) -> int:
    x = 1
    loop_size = 0
    while x != key:
        x = (x * PUBLIC_KEY_SUBJECT_NUMBER) % DIVISOR
        loop_size += 1
    return loop_size



def main():
    card_loop_size = loop_size_of_known_key(CARD_PUBLIC_KEY)
    encryption_key = transform_number(DOOR_PUBLIC_KEY, card_loop_size)
    print(encryption_key)


if __name__ == "__main__":
    main()
