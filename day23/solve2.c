#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#define PICKED_LEN 3
#define MAX_INITIAL_DATA_LEN 9
#define MAX_TOTAL_LEN 10000000

typedef struct{
    int total_len;
    int iterations;
    int data_len;
    int data[MAX_INITIAL_DATA_LEN];
} InputData;

// fills in InputData struct, returns 0 on failure, 1 on success
int parse_input(int argc, char **argv, InputData *in);

// returns dynamically allocated array of len total_len+1 or NULL pointer on error
uint32_t* init_followers(InputData *in);

// changes followers state according to the game rules
void play(uint32_t followers[], uint32_t current_item, int iterations);

uint32_t puzzle_answer2(uint32_t followers[]);

uint32_t select_destination(uint32_t current_item, int datalen, uint32_t picked[PICKED_LEN]);

int main(int argc, char **argv) {
    InputData input;
    if (!parse_input(argc, argv, &input)) {
        return -1;
    }
    printf("Running with: data %s (len %d), total_len %d, iterations %d\n",
            argv[1], input.data_len, input.total_len, input.iterations);
    int *followers = init_followers(&input);
    if (followers == NULL) {
        return -1;
    }
    printf("playing with followers:");
    for (int i = 0; i < input.total_len + 1; i++) {
        printf(" %d", followers[i]);
    }
    printf("\n");
    play(followers, input.data[0], input.iterations);
    printf("puzzle answer: %d\n", puzzle_answer2(followers));
    free(followers);
    return 0;
}

int parse_input(int argc, char **argv, InputData *in) {
    if (argc != 4) {
        printf("Usage: %s <data, eg. 716892543> <total_len> <iterations>\n", argv[0]);
        return 0;
    }
    in->total_len = atoi(argv[2]);
    if (in->total_len <= 0 || in->total_len > MAX_TOTAL_LEN) {
        printf("invalid total_len (argv[2]) %s\n", argv[2]);
        return 0;
    }
    in->iterations = atoi(argv[3]);
    if (in->iterations <= 0) {
        printf("invalid iterations (argv[3]) %s\n", argv[3]);
        return 0;
    }
    int i;
    char *data = argv[1];
    int min_data = MAX_INITIAL_DATA_LEN + 1; // will be overridden by the first valid number
    int max_data = -1; // will be overridden by the first valid number
    for (i = 0; data[i] != '\0'; i++) {
        char c = data[i];
        if (!isdigit(c) || c == '0') {
            printf("invalid character %c at index %d in input string %s - exptected only non-zero digits\n", c, i, data);
            return 0;
        }
        for (int j = 0; j < i; j++) {
            if (data[j] == c) {
                printf("input characters in data cannot repeat, got %c at index %d and %d\n", c, j, i);
                return 0;
            }
        }
        if (i > MAX_INITIAL_DATA_LEN) { // sanity check, it should not happen because we check that digits do not repeat
            printf("too long data string, max len is %d\n", MAX_INITIAL_DATA_LEN);
            return 0;
        }
        int d = c - '0'; // hacky conversion from digit to int by subtracting ASCII code
        if (d < min_data) {
            min_data = d;
        }
        if (d > max_data) {
            max_data = d;
        }
        in->data[i] = d;
    }
    if (min_data != 1 || max_data != i) {
        printf("invalid data, expected natural numbers from 1 to data_len (%d), got min %d, max %d, data %s\n",
               i, min_data, max_data, data); 
        return 0;
    }
    in->data_len = i;
    if (in->total_len < in->data_len) {
        printf("invalid total_len (%d) < data_len (%d)\n", in->total_len, in->data_len);
        return 0;
    }
    return 1;
}

uint32_t* init_followers(InputData *in) {
    // followers[a] = b -> it means that b is after a in the list.
    // It is another way of storing the circle of numbers, which allows to lookup numbers in O(1).
    // followers[0] will be unused - for simplicity of implementation I want to use 1-based indexing here.
    uint32_t *followers = (uint32_t*)malloc(sizeof(uint32_t) * (in->total_len + 1));
    if (followers == NULL) {
        return NULL;
    }
    memset(followers, 0, sizeof(uint32_t) * (in->total_len + 1));
    // set links between given elements: 1, 2, ..., len(data)-1
    for (int i = 1; i < in->data_len; i++) {
        int first = in->data[i - 1];
        int second = in->data[i];
        followers[first] = second;
    }
    if (in->total_len == in->data_len) { // special case for compatibility with part1
        // set link between last given element and first given element
        followers[in->data[in->data_len - 1]] = in->data[0];
    } else { // normal case for part2 - there are more elements than just given data
        //TODO
    }
    return followers;
}

void play(uint32_t followers[], uint32_t current_item, int iterations) {
    //TODO
}

uint32_t puzzle_answer2(uint32_t followers[]) {
    //TODO
    return 0;
}

uint32_t select_destination(uint32_t current_item, int datalen, uint32_t picked[PICKED_LEN]) {
    //TODO
    return 0;
}
