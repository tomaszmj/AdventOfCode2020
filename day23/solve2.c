#include <stdio.h>
#include <stdlib.h> 
#include <string.h>

#define PICKED_LEN 3

int* init_followers(char data[], int total_len);
void play(int followers[], int current_item, int iterations);
int puzzle_answer2(int followers[]);
int select_destination(int current_item, int datalen, int picked[PICKED_LEN]);


int main(int argc, char **argv) {
    if (argc != 4) {
        printf("Usage: %s <data, eg. 716892543> <total_len> <iterations>\n", argv[0]);
        return 1;
    }
    int total_len = atoi(argv[2]);
    int iterations = atoi(argv[3]);
    int data_len = strlen(argv[1]);
    printf("Running with: data %s (len %d), total_len %d, iterations %d\n", argv[1], data_len, total_len, iterations);
    return 0;
}

int* init_followers(char data[], int total_len) {
    return NULL;
}

void play(int followers[], int current_item, int iterations) {
}

int puzzle_answer2(int followers[]) {
    return 0;
}

int select_destination(int current_item, int datalen, int picked[PICKED_LEN]) {
    return 0;
}
