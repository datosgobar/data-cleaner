#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nomalizacion de strings
"""

import string


lower_words = [
    "el", "los", "la", "las",
    "de", "del", "en"
]

ignore_words = [
    "S/N"
]


def normalize_word(word):
    """Normaliza una palabra, capitalizándola cuando corresponde.

    Si contiene signos de puntacion se capitaliza dentro de esas strings.

    Args:
        word (str): Palabra

    Returns:
        str: Palabra normalizada
    """
    for character in string.punctuation:
        if character in word:
            return capitalize(word, sep=character)
    if word.lower() in ignore_words:
        return word
    if word.lower() in lower_words:
        return word.lower()
    return word.title()


def capitalize(string, sep=None):
    """Capitaliza una string que puede estar compuesta por varias palabras

    Args:
        string (str): Palabra
        sep (str): Separador

    Returns:
        str: String normalizada
    """
    words = unicode(string).split(sep)
    first_word = words[0].title()
    normalized_words = [first_word] + map(normalize_word, words[1:])

    return (sep if sep else " ").join(normalized_words)
