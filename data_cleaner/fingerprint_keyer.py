#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementa funciones para clusterizar strings.

Utiliza el algoritmo Key Collision: Fingerprint.
"""

import string
from unidecode import unidecode


def fingerprint_keyer(key_string):
    """Convierte un string en su fingerprint key representation.

    Args:
        key_string (str): String para convertir en fingerprint key.
    """
    # enforece string type
    if type(key_string) != str:
        key_string = unicode(key_string).encode('utf8')

    # remove leading and trailing whitespace, go to lowercase
    key_string = key_string.strip().lower()

    # remove all punctuation and control characters
    for punct in (set(key_string) & set(string.punctuation)):
        key_string = key_string.replace(punct, "")

    key_string = key_string.replace("\t", " ")

    # split the string into whitespace-separated tokens
    split_key = key_string.split()

    # sort the tokens and remove duplicates
    unique_sorted_split_key = sorted(set(split_key))

    # join the tokens back together
    finger_printed_key = " ".join(unique_sorted_split_key)

    # normalize extended western characters to their ASCII
    # representation (for example "gödel" → "godel")
    finger_printed_key = unidecode(finger_printed_key.decode("utf-8"))

    return finger_printed_key


def group_fingerprint_strings(inp):
    """Clusteriza un conjunto de strings, según sus fingerprints.

    Args:
        inp (list): Lista de strings.

    Returns:
        (dict, dict): En el primer dict las keys son los fingerprints y los
            valores las strings originales. En el segundo las keys son las
            strings sin normalizar y los valores el conteo de las strings
            originales.
    """
    res = {}
    counts = {}
    for (key, raw_str) in zip(map(fingerprint_keyer, inp), inp):
        res[key] = res.get(key, []) + [raw_str]
        counts[raw_str] = counts.get(raw_str, 0) + 1
    return res, counts


def get_best_replacements(d, counts):
    """
    Itera por cada cluster para determinar la mejor string para reemplazar las
    strings originales. De momento solo utiliza un conteo simple pero podria
    agregarse algun criterio basado en la capitalizacion de las palabras
    """
    res = {}
    for (k, v) in d.items():
        res[k] = max(v, key=lambda s: counts[s])
    return res


def replace_by_key(d, l):
    return [d.get(fingerprint_keyer(s), s) for s in l]
