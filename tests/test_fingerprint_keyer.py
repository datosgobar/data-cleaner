#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_fingerprint_keyer.py

Tests for `fingerprint_keyer.py` module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import unittest
import nose

from data_cleaner.fingerprint_keyer import fingerprint_keyer
from data_cleaner.fingerprint_keyer import group_fingerprint_strings
from data_cleaner.fingerprint_keyer import get_best_replacements
from data_cleaner.fingerprint_keyer import replace_by_key


class FingerprintKeyerIntegrationTestCase(unittest.TestCase):
    """Testea el funcionamiento conjunto de de fingerprint."""

    def test_fingerprint_methods_together(self):
        """Testea todos los métodos de fingerprint juntos."""
        inp_strings = ["DIGCE - Esmeralda 1212 - Piso 6° Of. 604",
                       "DIGCE - Esmeralda 1212 - Piso 6° Of. 604",
                       "DIGCE - Esmeralda 1212 - Piso 6° Of. 604",
                       "DIGCE - Esmeralda 1212 Piso 6° Of. 604",
                       "DIGCE - Esmeralda 1212 Piso 6° Of. 604"]

        clusters, counts = group_fingerprint_strings(inp_strings)
        replacements = get_best_replacements(clusters, counts)
        clean_strings = replace_by_key(replacements, inp_strings)
        exp_strings = ["DIGCE - Esmeralda 1212 - Piso 6° Of. 604"] * 5

        self.assertEqual(clean_strings, exp_strings)


class FingerprintKeyerUnitTestCase(unittest.TestCase):
    """Testea el funcionamiento de cada método del fingerprint keyer."""

    def test_fingerprint_keyer(self):
        """Testea la creación de una key fingerprint."""
        input_output_strings = [
            ("schön", "schon"),
            # ("Ære Øre Åre", "are aere ore"),
            # ("Straße","strasse"),
            #  test leading and trailing whitespace
            ("\tABC \t DEF ", "abc def"),
            ("bbb\taaa", "aaa bbb"),
            ("müller", "muller"),
            # ("müller","mueller"), # another possible interpretation
            # ("ﬁﬂĳ","fiflij"),
            # ("ﭏ","אל"),
            # ("œ ӕ","ae oe"),
            ("", ""),
        ]
        for inp_string, out_exp in input_output_strings:
            self.assertEqual(fingerprint_keyer(inp_string, True, True),
                             out_exp)

    def test_fingerprint_keyer_without_sorting(self):
        """Testea la creación de una key fingerprint sin ordenar los tokens."""
        input_output_strings = [
            ("bbb\taaa", "bbb aaa"),
            ("aaa\tbbb", "aaa bbb"),
        ]
        for inp_string, out_exp in input_output_strings:
            self.assertEqual(fingerprint_keyer(inp_string, False, False),
                             out_exp)

    def test_fingerprint_keyer_without_removing_dups(self):
        """Testea la creación de una key fingerprint sin ordenar los tokens."""
        input_output_strings = [
            ("bbb\taaa bbb", "bbb aaa bbb"),
            ("aaa\tbbb bbb", "aaa bbb bbb"),
        ]
        for inp_string, out_exp in input_output_strings:
            self.assertEqual(fingerprint_keyer(inp_string, False, False),
                             out_exp)

    def test_group_fingerprint_strings(self):
        """Testea el agrupamiento de strings, por su fingerpint."""
        input_strings = [
            " - juan     peRes",
            "Juan ; Perés",
            "Juan -- Peres",
            "Juan Per\tes",
            "juán Peres",
            "Juan Peres",
            "Juan Peres",
            "   Juan\t \tPeres",
        ]
        exp_clusters = {'es juan per': ['Juan Per\tes'],
                        'juan peres': [' - juan     peRes',
                                       'Juan ; Per\xe9s',
                                       'Juan -- Peres',
                                       'ju\xe1n Peres',
                                       'Juan Peres',
                                       'Juan Peres',
                                       '   Juan\t \tPeres']}
        exp_counts = {'   Juan\t \tPeres': 1,
                      ' - juan     peRes': 1,
                      'Juan -- Peres': 1,
                      'Juan ; Per\xe9s': 1,
                      'Juan Per\tes': 1,
                      'Juan Peres': 2,
                      'ju\xe1n Peres': 1}
        clusters, counts = group_fingerprint_strings(input_strings, True,
                                                     True)

        self.assertEqual(clusters, exp_clusters)
        self.assertEqual(counts, exp_counts)

    def test_get_best_replacements(self):
        """Testea la toma de los mejores strings de cada cluster."""
        clusters = {'es juan per': ['Juan Per\tes'],
                    'juan peres': [' - juan     peRes',
                                   'Juan ; Per\xe9s',
                                   'Juan -- Peres',
                                   'ju\xe1n Peres',
                                   'Juan Peres',
                                   'Juan Peres',
                                   '   Juan\t \tPeres']}
        counts = {'   Juan\t \tPeres': 1,
                  ' - juan     peRes': 1,
                  'Juan -- Peres': 1,
                  'Juan ; Per\xe9s': 1,
                  'Juan Per\tes': 1,
                  'Juan Peres': 2,
                  'ju\xe1n Peres': 1}
        exp_replacements = {'es juan per': 'Juan Per\tes',
                            'juan peres': 'Juan Peres'}
        replacements = get_best_replacements(clusters, counts)

        self.assertEqual(replacements, exp_replacements)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
