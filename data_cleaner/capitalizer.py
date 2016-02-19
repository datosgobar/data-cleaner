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


def normalize_word(w):
    """Normaliza el cade una palabra. Si contiene signos de puntacion se
    capitaliza dentro de esas strings.
    Args:
        w (str): Palabra
    Returns:
        str: Palabra normalizada
    """
    for c in string.punctuation:
        if c in w:
            return capitalize(w, sep=c)
    if w.lower() in ignore_words:
        return w
    if w.lower() in lower_words:
        return w.lower()
    return w.title()


def capitalize(s, sep=None):
    """Capitaliza una string que puede estar compuesta por varias palabras
    Args:
        w (str): Palabra
        sep (str): Separador
    Returns:
        str: String normalizada
    """
    l = s.split(sep)
    l = map(str.title, l[:1]) + map(normalize_word, l[1:])
    return (sep if sep else " ").join(l)
