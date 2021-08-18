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

// functions for changing followers state according to the game rules
void play(uint32_t followers[], int total_len, uint32_t current_item, int iterations);
uint32_t select_destination(uint32_t current_item, int total_len, uint32_t picked[PICKED_LEN]);
int x_in_picked(uint32_t x, uint32_t picked[PICKED_LEN]);

// functions for shownig output
void print_followers(uint32_t followers[], int total_len);
void print_all_elements(uint32_t followers[], int total_len, int start);
uint64_t puzzle_answer2(uint32_t followers[]);


int main(int argc, char **argv) {
    InputData input;
    if (!parse_input(argc, argv, &input)) {
        return -1;
    }
    printf("Running with: data %s (len %u), total_len %u, iterations %u\n",
           argv[1], input.data_len, input.total_len, input.iterations);
    int *followers = init_followers(&input);
    if (followers == NULL) {
        return -1;
    }
    if (input.total_len < 100) {
        print_followers(followers, input.total_len);
    }
    play(followers, input.total_len, input.data[0], input.iterations);
    if (input.total_len < 100) {
        print_all_elements(followers, input.total_len, 1);
    }
    printf("%lu\n", puzzle_answer2(followers));
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
    if (in->iterations < 0) {
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
            printf("invalid character %c at index %u in input string %s - exptected only non-zero digits\n", c, i, data);
            return 0;
        }
        for (int j = 0; j < i; j++) {
            if (data[j] == c) {
                printf("input characters in data cannot repeat, got %c at index %u and %u\n", c, j, i);
                return 0;
            }
        }
        if (i > MAX_INITIAL_DATA_LEN) { // sanity check, it should not happen because we check that digits do not repeat
            printf("too long data string, max len is %u\n", MAX_INITIAL_DATA_LEN);
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
        printf("invalid data, expected natural numbers from 1 to data_len (%u), got min %d, max %d, data %s\n",
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
    uint32_t *followers = malloc(sizeof(uint32_t) * (in->total_len + 1));
    if (followers == NULL) {
        return NULL;
    }
    memset(followers, 0, sizeof(uint32_t) * (in->total_len + 1));
    for (int i = 1; i < in->data_len; i++) {
        // set links between given elements: 1, 2, ..., data_len
        int first = in->data[i - 1];
        int second = in->data[i];
        followers[first] = second;
    }
    if (in->total_len == in->data_len) { // special case for compatibility with part1
        // set link between last given element and first given element
        followers[in->data[in->data_len - 1]] = in->data[0];
    } else { // normal case for part2 - there are more elements than just given data
        followers[in->data[in->data_len - 1]] = in->data_len + 1; // link between last given element and first generated
        for (int x = in->data_len + 1; x < in->total_len; x++) { // links between generated elements
            followers[x] = x + 1;
        }
        followers[in->total_len] = in->data[0]; // link between last generated element and first given
    }
    return followers;
}

void play(uint32_t followers[], int total_len, uint32_t current_item, int iterations) {
    int picked[PICKED_LEN];
    for (int i = 0; i < iterations; i++) {
        int item = current_item; // variable used to iterate over followers
        // move 3 items after current_item to picked list:
        for (int j = 0; j < PICKED_LEN; j++) {
            item = followers[item];
            picked[j] = item;
        }
        followers[current_item] = followers[picked[PICKED_LEN -1]]; // virtually remove picked items
        // find destination for picked items:
        item = select_destination(current_item, total_len, picked);
        uint32_t after_destination = followers[item];
        // add previously removed items after destination:
        for (int j = 0; j < PICKED_LEN; j++) {
            followers[item] = picked[j];
            item = picked[j];
        }
        followers[picked[PICKED_LEN -1]] = after_destination;
        // advance current_item:
        current_item = followers[current_item];
    }
}

void print_followers(uint32_t followers[], int total_len) {
    printf("followers:");
    for (int i = 0; i < total_len + 1; i++) {
        printf(" %d", followers[i]);
    }
    printf("\n");
}

void print_all_elements(uint32_t followers[], int total_len, int start) {
    printf("all elements:");
    int i = 0;
    int max_i = total_len - 1;
    uint32_t curr = start;
    for(;;) {
        if (i >= max_i) {
            printf("\nWARNING looping through followers stopped because reached max len (%d)", max_i);
            return;
        }
        printf(" %d", curr);
        curr = followers[curr];
        if (curr == start) {
            printf("\n");
            return;
        }
    }
}

uint64_t puzzle_answer2(uint32_t followers[]) {
    uint32_t after1 = followers[1];
    uint32_t afterafter1 = followers[after1];
    return (uint64_t)after1 * (uint64_t)afterafter1;
}

uint32_t select_destination(uint32_t current_item, int total_len, uint32_t picked[PICKED_LEN]) {
    int x = current_item - 1;
    if (x <= 0) {
        x = total_len;
    }
    for (;;) {
        if (!x_in_picked(x, picked)) {
            return x;
        }
        if (--x == 0) {
            x = total_len;
        }
    }
}

int x_in_picked(uint32_t x, uint32_t picked[PICKED_LEN]) {
    for (int j = 0; j < PICKED_LEN; j++) {
        if (x == picked[j]) {
            return 1;
        }
    }
    return 0;
}
