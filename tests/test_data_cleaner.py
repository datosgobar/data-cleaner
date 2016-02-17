#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_data_cleaner.py

Unit tests for `data_cleaner.py` module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import unittest
import nose
import os
import pandas as pd

from data_cleaner import DataCleaner

BASE_DIR = os.path.dirname(__file__)


class DataCleanerTestCase(unittest.TestCase):
    """Testea reglas de limpieza del DataCleaner."""

    def setUp(self):
        self.input_dir = os.path.join(BASE_DIR, "input")
        self.output_dir = os.path.join(BASE_DIR, "output")

    def get_input(self, case_name):
        file_name = "to_clean_" + case_name + ".csv"
        return os.path.join(self.input_dir, file_name)

    def get_output(self, case_name):
        file_name = "clean_" + case_name + ".csv"
        return os.path.join(self.output_dir, file_name)

    def test_nombre_propio(self):
        input_path = self.get_input("nombre_propio")
        output_path = self.get_input("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.nombre_propio(field)
        res = list(series[0])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp = list(df[field])

        self.assertEqual(res, exp)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
