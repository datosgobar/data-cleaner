#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementa funciones para clusterizar strings.

Utiliza el algoritmo Key Collision: Fingerprint.
"""

import string
from unidecode import unidecode
from functools import partial
import pandas as pd


def fingerprint_keyer(key_string, sort_tokens=False, remove_duplicates=False):
    """Convierte un string en su fingerprint key representation.

    Args:
        key_string (str): String para convertir en fingerprint key.

    Returns:
        str: Fingerprint correspondiente al input.
    """
    if pd.isnull(key_string):
        return pd.np.nan

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

    # remove duplicates, if chosen
    if remove_duplicates:
        dups_removed = set(split_key)
    else:
        dups_removed = split_key

    # sort the tokens, if chosen
    if sort_tokens:
        # sort the tokens
        sorted_split_key = sorted(dups_removed)
    else:
        sorted_split_key = dups_removed

    # join the tokens back together
    finger_printed_key = " ".join(sorted_split_key)

    # normalize extended western characters to their ASCII
    # representation (for example "gödel" → "godel")
    finger_printed_key = unidecode(finger_printed_key.decode("utf-8"))

    return finger_printed_key


def group_fingerprint_strings(raw_strs, sort_tokens=False,
                              remove_duplicates=False):
    """Clusteriza un conjunto de strings, según sus fingerprints.

    Args:
        raw_strs (list): Lista de strings sin procesar.

    Returns:
        (dict, dict): En el primer dict las keys son los fingerprints y los
            valores las strings originales. En el segundo las keys son las
            strings sin normalizar y los valores el conteo de la cantidad de
            veces que aparecen.
    """
    res = {}
    counts = {}
    fingerprint_keyer_with_args = partial(fingerprint_keyer,
                                          sort_tokens=sort_tokens,
                                          remove_duplicates=remove_duplicates)
    for (key, raw_str) in zip(map(fingerprint_keyer_with_args, raw_strs),
                              raw_strs):
        res[key] = res.get(key, []) + [raw_str]
        counts[raw_str] = counts.get(raw_str, 0) + 1
    return res, counts


def get_best_replacements(clusters, counts):
    """Selecciona los strings más utilizados por cluster.

    Itera por cada cluster para determinar la mejor string para reemplazar las
    strings originales. De momento solo utiliza un conteo simple pero podria
    agregarse algun criterio basado en la capitalizacion de las palabras

    Args:
        clusters (dict): {fingerprint: [raw_string_1, raw_string_2]}
        counts (dict): {raw_string: cant_veces_utilizada}

    Returns:
        dict: {fingerprint: string_mas_usada_para_esa_fingerprint}
    """
    res = {}
    for (fingerprint, key_strings) in clusters.items():
        res[fingerprint] = max(key_strings, key=lambda s: counts[s])
    return res


def replace_by_key(replacements, raw_strs):
    """Reemplaza strings por sus mejores equivalentes."""
    return [replacements.get(fingerprint_keyer(s), s) for s in raw_strs]
