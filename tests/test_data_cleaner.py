#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_data_cleaner.py

Unit tests for `data_cleaner.py` module. Si los tests no corren, correr desde
la línea de comandos: `chmod 644 test_data_cleaner.py`
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
        output_path = self.get_output("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.nombre_propio(field)
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_string_normal(self):
        input_path = self.get_input("string_normal")
        output_path = self.get_output("string_normal")
        field = "lugar_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.string(field)
        res = list(series[0])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_fecha_completa(self):
        input_path = self.get_input("fecha_completa")
        output_path = self.get_output("fecha_completa")
        field = "fecha_completa_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_completa(field, "DD-MM-YYYY HH:mm")
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp = list(df["isodatetime_" + field])

        self.assertEqual(res, exp)

    def test_fecha_separada(self):
        input_path = self.get_input("fecha_separada")
        output_path = self.get_output("fecha_separada")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_separada([
            ["fecha_audiencia", "DD-MM-YYYY"],
            ["hora_audiencia", "HH:mm"]
        ],
            "audiencia")
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp = list(df["isodatetime_audiencia"])

        self.assertEqual(res, exp)

    def test_string_simple_split(self):
        input_path = self.get_input("string_separable_simple")
        output_path = self.get_output("string_separable_simple")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.string_simple_split(
            "sujeto_obligado",
            [", Cargo:", "Cargo:"],
            ["nombre", "cargo"]
        )
        res_1 = list(series[0])
        res_2 = list(series[1])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp_1 = list(df["sujeto_obligado_nombre"])
        exp_2 = list(df["sujeto_obligado_cargo"])

        self.assertEqual(res_1, exp_1)
        self.assertEqual(res_2, exp_2)

    @unittest.skip("skip")
    def test_string_regex_split(self):
        pass

    def test_string_peg_split(self):
        input_path = self.get_input("string_separable_complejo")
        output_path = self.get_output("string_separable_complejo")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.string_peg_split(
            "solicitante",
            """
            allowed_char = anything:x ?(x not in '1234567890() ')
            nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
            number = <digit+>:num -> int(num)

            nom_comp = <nombre+>:nc -> nc.strip()
            cargo = '(' <nombre+>:c ')' -> c.strip()
            dni = ','? ws 'DNI' ws number:num -> num

            values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
            """,
            ["nombre", "cargo", "dni"]
        )
        res_1 = list(series[0])
        res_2 = list(series[1])
        res_3 = list(series[2])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path)
        exp_1 = list(df["solicitante_nombre"])
        exp_2 = list(df["solicitante_cargo"])
        exp_3 = list(df["solicitante_dni"])

        self.assertEqual(res_1, exp_1)
        self.assertEqual(res_2, exp_2)
        self.assertEqual(res_3, exp_3)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
