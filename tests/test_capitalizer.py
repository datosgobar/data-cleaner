#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_capitalizer.py

Tests for `capitalizer.py` module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import unittest
import nose

import sys
sys.path.insert(0, '')

from data_cleaner.capitalizer import normalize_word
from data_cleaner.capitalizer import capitalize


class CapitalizerIntegrationTestCase(unittest.TestCase):
    """Testea el funcionamiento conjunto de capitalizer."""

    def test_capitalizer_methods_together(self):
        """Testea el método principal de normalizecion."""
        test_strings = [
            ("JUAN PEREZ", "Juan Perez"),
            ("juAn PErez", "Juan Perez"),
            (u"juán PErez", u'Ju\xe1n Perez'),
            (u"o'higgins", u"O'Higgins"),
            (u"o'higgins mc Donald", u"O'Higgins Mc Donald"),
            ("Juan De La Vaca", 'Juan de la Vaca'),
            (u"Calle PúBlica S/N", u"Calle Pública S/N"),
            (1, "1"),
            (1.5, "1.5"),
        ]
        for (inp, outp) in test_strings:
            self.assertEqual(capitalize(inp), outp)


class CapitalizerKeyerUnitTestCase(unittest.TestCase):
    """Testea el funcionamiento de cada método del Capitalizer."""

    def test_normalize_word(self):
        """Testea la normalizacion de una string."""
        test_strings = [
            ("JUAN", "Juan"),
            ("juAn", "Juan"),
            (u"juán", u'Ju\xe1n'),
            (u"o'higgins", u"O'Higgins"),
            (u"S/N", u"S/N"),
            (u"DE", u"de"),
        ]
        for (inp, outp) in test_strings:
            self.assertEqual(normalize_word(inp), outp)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
