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


class FingerprintKeyerTestCase(unittest.TestCase):
    """Tests for FingerprintKeyer class."""

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
            self.assertEqual(fingerprint_keyer(inp_string), out_exp)

    def test_group_fingerprint_strings(self):
        """Testea el agrupamiento de strings, por su fingerpint."""
        input_strings = [
            u" - juan     peRes",
            u"Juan ; Perés",
            u"Juan -- Peres",
            u"Juan Per\tes",
            u"juán Peres",
            u"Juan Peres",
            u"Juan Peres",
            u"   Juan\t \tPeres",
        ]
        exp_clusters = {'es juan per': [u'Juan Per\tes'],
                        'juan peres': [u' - juan     peRes',
                                       u'Juan ; Per\xe9s',
                                       u'Juan -- Peres',
                                       u'ju\xe1n Peres',
                                       u'Juan Peres',
                                       u'Juan Peres',
                                       u'   Juan\t \tPeres']}
        exp_counts = {u'   Juan\t \tPeres': 1,
                      u' - juan     peRes': 1,
                      u'Juan -- Peres': 1,
                      u'Juan ; Per\xe9s': 1,
                      u'Juan Per\tes': 1,
                      u'Juan Peres': 2,
                      u'ju\xe1n Peres': 1}
        clusters, counts = group_fingerprint_strings(input_strings)

        self.assertEqual(clusters, exp_clusters)
        self.assertEqual(counts, exp_counts)

    def test_get_best_replacements(self):
        """Testea la toma de los mejores strings de cada cluster."""
        clusters = {'es juan per': [u'Juan Per\tes'],
                    'juan peres': [u' - juan     peRes',
                                   u'Juan ; Per\xe9s',
                                   u'Juan -- Peres',
                                   u'ju\xe1n Peres',
                                   u'Juan Peres',
                                   u'Juan Peres',
                                   u'   Juan\t \tPeres']}
        counts = {u'   Juan\t \tPeres': 1,
                  u' - juan     peRes': 1,
                  u'Juan -- Peres': 1,
                  u'Juan ; Per\xe9s': 1,
                  u'Juan Per\tes': 1,
                  u'Juan Peres': 2,
                  u'ju\xe1n Peres': 1}
        exp_replacements = {'es juan per': u'Juan Per\tes',
                            'juan peres': u'Juan Peres'}
        replacements = get_best_replacements(clusters, counts)

        self.assertEqual(replacements, exp_replacements)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
