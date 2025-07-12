#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>


// Base64 character set
const char *base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

void encryptDecrypt(char *input, char *output, size_t length) {
    char key[] = {'K', 'C', 'Q', 'B', 'H'}; //Can be any chars, and any size array
    size_t key_len = sizeof(key)/sizeof(char);

    for(size_t i = 0; i < length; i++) {
        output[i] = input[i] ^ key[i % key_len];
    }
    // No need to null-terminate here, as the caller (Encrypt/Decode) will do it if needed for a string.
}


// Function to encode a binary buffer into Base64
char *base64_encode(const unsigned char *data, size_t input_length) {
    size_t output_length = 4 * ((input_length + 2) / 3);
    char *encoded_data = (char *)malloc(output_length + 1); // +1 for null terminator
    if (encoded_data == NULL) {
        return NULL; // Memory allocation failed
    }

    // Loop through the input data and encode it to Base64
    for (size_t i = 0, j = 0; i < input_length;) {
        // Extract three octets from input data (or use zero padding)
        uint32_t octet_a = i < input_length ? data[i++] : 0;
        uint32_t octet_b = i < input_length ? data[i++] : 0;
        uint32_t octet_c = i < input_length ? data[i++] : 0;

        // Combine three octets into a 24-bit triple
        uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

        // Encode triple as Base64 characters
        encoded_data[j++] = base64_chars[(triple >> 18) & 0x3F];
        encoded_data[j++] = base64_chars[(triple >> 12) & 0x3F];
        encoded_data[j++] = base64_chars[(triple >> 6) & 0x3F];
        encoded_data[j++] = base64_chars[triple & 0x3F];
    }

    // Handle padding and null-terminate the encoded string
    // The loop condition should be `output_length` after the padding characters are potentially added.
    // The current loop below removes padding, but base64_decode expects padding to exist for correct length calculation sometimes.
    // For simplicity and correct decoding, we'll keep the padding characters ('=') and just null-terminate at the calculated output_length.
    if (input_length % 3 == 1) {
        encoded_data[output_length - 2] = '=';
        encoded_data[output_length - 1] = '=';
    } else if (input_length % 3 == 2) {
        encoded_data[output_length - 1] = '=';
    }
    encoded_data[output_length] = '\0';

    return encoded_data;
}

// Function to decode a Base64 encoded string into binary data
unsigned char *base64_decode(const char *input, size_t *output_length) {
    size_t input_length = strlen(input);
    if (input_length % 4 != 0) {
        // Base64 string must have a length that is a multiple of 4
        // (after removing whitespace if any, which this simple function doesn't handle)
        return NULL;
    }

    // Calculate the expected output length
    *output_length = (input_length / 4) * 3;
    if (input[input_length - 1] == '=') {
        (*output_length)--;
    }
    if (input[input_length - 2] == '=') {
        (*output_length)--;
    }

    // Allocate memory for the decoded data
    unsigned char *decoded_data = (unsigned char *)malloc(*output_length + 1); // +1 for potential null terminator if treated as string
    if (decoded_data == NULL) {
        return NULL; // Memory allocation failed
    }

    size_t j = 0; // Index for decoded_data
    for (size_t i = 0; i < input_length; i += 4) {
        uint32_t val = 0;
        for (int k = 0; k < 4; k++) {
            char c = input[i + k];
            const char *char_pointer = strchr(base64_chars, c);
            if (c == '=') {
                val = (val << 6); // Padding, effectively 0 for the 6 bits
            } else if (char_pointer != NULL) {
                val = (val << 6) | (char_pointer - base64_chars);
            } else {
                free(decoded_data);
                return NULL; // Invalid Base64 character
            }
        }
        decoded_data[j++] = (val >> 16) & 0xFF;
        if (input[i+2] != '=') { // Only add second byte if not padded with two '='
            decoded_data[j++] = (val >> 8) & 0xFF;
        }
        if (input[i+3] != '=') { // Only add third byte if not padded with one '='
            decoded_data[j++] = val & 0xFF;
        }
    }
    decoded_data[j] = '\0'; // Null-terminate the decoded binary data

    return decoded_data;
}

char* Encrypt(char* input){
    char *xored_output = NULL;
    char *ciphertext_b64 = NULL;

    size_t input_length = strlen(input);

    // Allocate memory for the XORed output. The output size is the same as the input.
    xored_output = (char *)malloc(input_length + 1); // +1 for null terminator if needed, though not used by encryptDecrypt directly
    if (xored_output == NULL) {
        return NULL; // Memory allocation failed
    }

    // Perform XOR encryption
    encryptDecrypt(input, xored_output, input_length);

    // Base64 encode the XORed data (which is now binary data)
    // The base64_encode function expects unsigned char* for its data input.
    ciphertext_b64 = base64_encode((const unsigned char *)xored_output, input_length);

    free(xored_output); // Free the temporary XORed buffer

    return ciphertext_b64; // Caller is responsible for freeing this memory
}

char* Decode(char* input){
    char *plaintext = NULL;
    size_t decoded_b64_length; // This will be the actual length of the binary data after Base64 decoding
    unsigned char *decoded_b64_output = base64_decode(input, &decoded_b64_length);

    if (decoded_b64_output == NULL) {
        return NULL; // Handle base64_decode errors (e.g., invalid input)
    }

    // Allocate memory for the plaintext (after XOR decryption).
    // The size should be exactly what base64_decode returned as `decoded_b64_length` plus one for the null terminator.
    plaintext = (char *)malloc(decoded_b64_length + 1);
    if (plaintext == NULL) {
        free(decoded_b64_output);
        return NULL; // Handle memory allocation failure
    }

    // Perform XOR decryption on the decoded Base64 data.
    // The length passed to encryptDecrypt must be `decoded_b64_length`.
    encryptDecrypt((char *)decoded_b64_output, plaintext, decoded_b64_length);

    // CRITICAL FIX: Null-terminate the plaintext string
    plaintext[decoded_b64_length] = '\0';

    free(decoded_b64_output); // Free the temporary decoded Base64 buffer

    return plaintext; // Caller is responsible for freeing this memory
}
