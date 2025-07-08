#!/bin/bash

# Function to convert a string to a character array
# Usage: string_to_char_array "your string here"
string_to_char_array() {
    local input_string="$1"
    local -a char_array=() # Declare an empty array

    # Loop through each character of the string
    for (( i=0; i<${#input_string}; i++ )); do
        char_array+=("${input_string:$i:1}") # Append each character to the array
    done

    # Print the array elements, each enclosed in single quotes and separated by a comma and space.
    # This format matches the user's requested output: 'h', 'e', 'l', 'l', 'o', ...
    local output=""
    for char in "${char_array[@]}"; do
        if [[ -n "$output" ]]; then
            output+=", "
        fi
        output+="'$char'"
    done
    echo "$output"
}

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"<your string>\""
    echo "Example: $0 \"hello world\""
    exit 1
fi

# Get the string from the first command-line argument
MY_STRING="$1"

echo "Original string: \"$MY_STRING\""
echo "Converted array format:"
string_to_char_array "$MY_STRING"

# The previous hardcoded example is removed as the script now expects user input.
# If you want to keep additional examples, you can add them back using fixed strings.
