#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Este módulo fue tomado de:
    https://github.com/tweirick/okstate_bioinformatics_command_line_programs/blob/master/misc_programs/FingerprintKeyer.py

10/23/2012 Tyler Weirick
An implementation of Google-Refine's FingerprintKeyer algorithm in Python
written mostly because just about every site with a library I could use is down
today.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement

import string
# For the translate make a dictionary and do replaces based on the difference
# of chars
#=============================================================================
tranlate_dict = {'\\u00C0': 'a', '\\u00C1': 'a', '\\u00C2': 'a', '\\u00C3': 'a',
                 '\\u00C4': 'a', '\\u00C5': 'a', '\\u00E0': 'a', '\\u00E1': 'a', '\\u00E2': 'a', '\\u00E3': 'a',
                 '\\u00E4': 'a', '\\u00E5': 'a', '\\u0100': 'a', '\\u0101': 'a', '\\u0102': 'a', '\\u0103': 'a',
                 '\\u0104': 'a', '\\u0105': 'a',
                 '\\u00C7': 'c', '\\u00E7': 'c', '\\u0106': 'c', '\\u0107': 'c', '\\u0108': 'c', '\\u0109': 'c',
                 '\\u010A': 'c', '\\u010B': 'c', '\\u010C': 'c', '\\u010D': 'c',
                 '\\u00D0': 'd', '\\u00F0': 'd', '\\u010E': 'd', '\\u010F': 'd', '\\u0110': 'd', '\\u0111': 'd',
                 '\\u00C8': 'e', '\\u00C9': 'e', '\\u00CA': 'e', '\\u00CB': 'e', '\\u00E8': 'e', '\\u00E9': 'e',
                 '\\u00EA': 'e', '\\u00EB': 'e', '\\u0112': 'e', '\\u0113': 'e', '\\u0114': 'e', '\\u0115': 'e',
                 '\\u0116': 'e', '\\u0117': 'e', '\\u0118': 'e', '\\u0119': 'e', '\\u011A': 'e', '\\u011B': 'e',
                 '\\u011C': 'g', '\\u011D': 'g', '\\u011E': 'g', '\\u011F': 'g', '\\u0120': 'g', '\\u0121': 'g',
                 '\\u0122': 'g', '\\u0123': 'g',
                 '\\u0124': 'h', '\\u0125': 'h', '\\u0126': 'h', '\\u0127': 'h',
                 '\\u00CC': 'i', '\\u00CD': 'i', '\\u00CE': 'i', '\\u00CF': 'i', '\\u00EC': 'i', '\\u00ED': 'i',
                 '\\u00EE': 'i', '\\u00EF': 'i', '\\u0128': 'i', '\\u0129': 'i', '\\u012A': 'i', '\\u012B': 'i',
                 '\\u012C': 'i', '\\u012D': 'i', '\\u012E': 'i', '\\u012F': 'i', '\\u0130': 'i', '\\u0131': 'i',
                 '\\u0134': 'j', '\\u0135': 'j',
                 '\\u0136': 'k', '\\u0137': 'k', '\\u0138': 'k',
                 '\\u0139': 'l', '\\u013A': 'l', '\\u013B': 'l', '\\u013C': 'l', '\\u013D': 'l', '\\u013E': 'l',
                 '\\u013F': 'l', '\\u0140': 'l', '\\u0141': 'l', '\\u0142': 'l',
                 '\\u00D1': 'n', '\\u00F1': 'n', '\\u0143': 'n', '\\u0144': 'n', '\\u0145': 'n', '\\u0146': 'n',
                 '\\u0147': 'n', '\\u0148': 'n', '\\u0149': 'n', '\\u014A': 'n', '\\u014B': 'n',
                 '\\u00D2': 'o', '\\u00D3': 'o', '\\u00D4': 'o', '\\u00D5': 'o', '\\u00D6': 'o', '\\u00D8': 'o',
                 '\\u00F2': 'o', '\\u00F3': 'o', '\\u00F4': 'o', '\\u00F5': 'o', '\\u00F6': 'o', '\\u00F8': 'o',
                 '\\u014C': 'o', '\\u014D': 'o', '\\u014E': 'o', '\\u014F': 'o', '\\u0150': 'o', '\\u0151': 'o',
                 '\\u0154': 'r', '\\u0155': 'r', '\\u0156': 'r', '\\u0157': 'r', '\\u0158': 'r', '\\u0159': 'r',
                 '\\u015A': 's', '\\u015B': 's', '\\u015C': 's', '\\u015D': 's', '\\u015E': 's', '\\u015F': 's',
                 '\\u0160': 's', '\\u0161': 's', '\\u017F': 's',
                 '\\u0162': 't', '\\u0163': 't', '\\u0164': 't', '\\u0165': 't', '\\u0166': 't', '\\u0167': 't',
                 '\\u00D9': 'u', '\\u00DA': 'u', '\\u00DB': 'u', '\\u00DC': 'u', '\\u00F9': 'u', '\\u00FA': 'u',
                 '\\u00FB': 'u', '\\u00FC': 'u', '\\u0168': 'u', '\\u0169': 'u', '\\u016A': 'u', '\\u016B': 'u',
                 '\\u016C': 'u', '\\u016D': 'u', '\\u016E': 'u', '\\u016F': 'u', '\\u0170': 'u', '\\u0171': 'u',
                 '\\u0172': 'u', '\\u0173': 'u',
                 '\\u0174': 'w', '\\u0175': 'w',
                 '\\u00DD': 'y', '\\u00FD': 'y', '\\u00FF': 'y', '\\u0176': 'y', '\\u0177': 'y', '\\u0178': 'y',
                 '\\u0179': 'z', '\\u017A': 'z', '\\u017B': 'z', '\\u017C': 'z', '\\u017D': 'z', '\\u017E': 'z'}


def finger_print_keyer(key_string):
    assert type(key_string) == str, "ERROR: key must be a string."

    # remove leading and trailing whitespace
    key_string = key_string.strip().lower()

    # change all characters to their lower case representation
    key_string = key_string.lower()

    # remove all punctuation and control characters
    for punct in (set(key_string) & set(string.punctuation)):
        key_string = key_string.replace(punct, "")

    # split the string into whitespace-separated tokens
    split_key = key_string.split()

    # sort the tokens and remove duplicates
    unique_sorted_split_key = sorted(set(split_key))

    # join the tokens back together
    finger_printed_key = "".join(unique_sorted_split_key)

    # normalize extended western characters to their ASCII
    # representation (for example "gödel" → "godel")
    # Leaving this out for now as it should not matter for protein names.
    # translate()
    return finger_printed_key
