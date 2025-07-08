#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "enc.h"

int main(int argc, char *argv[]) {
    char *input = NULL;
    char *output = NULL;
    char *ciphertext = NULL;
    char *plaintext = NULL;

    if (argc < 3) {
        printf("Usage: %s <encode|decode> <data>\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "encode") == 0) {
        input = argv[2];
        ciphertext = Encrypt(input);
        printf("%s", ciphertext);
        return 0;
    } else if (strcmp(argv[1], "decode") == 0) {
        input = argv[2];
        plaintext = Decode(input);
        printf("%s", plaintext);
        return 0;
    } else {
        printf("Invalid operation. Use 'encode' or 'decode'.\n");
        return 1;
    }

    return 0;
}