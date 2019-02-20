#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Nomalizacion de strings."""

import string
import pandas as pd
from functools import partial
import six


LOWER_WORDS = [
    "el", "los", "la", "las",
    "de", "del", "en", "y"
]

IGNORE_WORDS = [
    "S/N"
]


def normalize_word(word, lower_words=None):
    """Normaliza una palabra, capitalizándola cuando corresponde.

    Si contiene signos de puntacion se capitaliza dentro de esas strings.

    Args:
        word (str): Palabra

    Returns:
        str: Palabra normalizada
    """
    lower_words = lower_words or LOWER_WORDS

    for character in string.punctuation:
        if character in word:
            return capitalize(word, sep=character)
    if word.lower() in IGNORE_WORDS:
        return word
    if word.lower() in lower_words:
        return word.lower()
    return word.title()


def capitalize(string, sep=None, encoding="utf-8", lower_words=None):
    """Capitaliza una string que puede estar compuesta por varias palabras

    Args:
        string (str): Palabra
        sep (str): Separador

    Returns:
        str: String normalizada
    """
    if pd.isnull(string):
        return pd.np.nan

    if not isinstance(string, six.text_type):
        string = six.text_type(string)

    words = string.split(sep)
    if len(words) == 0:
        return ""
    first_word = words[0].title()
    partial_normalize_word = partial(normalize_word, lower_words=lower_words)
    normalized_words = [first_word] + list(map(partial_normalize_word, words[1:]))

    return (sep if sep else " ").join(normalized_words)
