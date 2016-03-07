#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Nomalizacion de strings."""

import string


LOWER_WORDS = [
    "el", "los", "la", "las",
    "de", "del", "en", "y"
]

IGNORE_WORDS = [
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
    if word.lower() in IGNORE_WORDS:
        return word
    if word.lower() in LOWER_WORDS:
        return word.lower()
    return word.title()


def capitalize(string, sep=None, encoding="utf-8"):
    """Capitaliza una string que puede estar compuesta por varias palabras

    Args:
        string (str): Palabra
        sep (str): Separador

    Returns:
        str: String normalizada
    """
    if type(string) is not str or type(string) is not unicode:
        string = unicode(string)

    words = string.split(sep)
    if len(words) == 0:
        return ""
    first_word = words[0].title()
    normalized_words = [first_word] + map(normalize_word, words[1:])

    return (sep if sep else " ").join(normalized_words)
