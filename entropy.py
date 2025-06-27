#!/bin/python3
# Usage: python3 entropy.py <file>

import math, sys

def entropy(string):
    "Calculates the Shannon entropy of a UTF-8 encoded string"

    # decode the string as UTF-8
    unicode_string = string.decode('utf-8')

    # get probability of chars in string
    prob = [ float(unicode_string.count(c)) / len(unicode_string) for c in dict.fromkeys(list(unicode_string)) ]

    # calculate the entropy
    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])

    return entropy


f = open(sys.argv[1], 'rb')
content = f.read()
f.close()

print(entropy(content))
