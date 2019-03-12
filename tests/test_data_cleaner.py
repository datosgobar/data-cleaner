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
import vcr
import geopandas as gpd
import sys
sys.path.insert(0, '')
from data_cleaner import DataCleaner
from data_cleaner.data_cleaner import DuplicatedField
from .rules.integration import rules
import csv
import six

BASE_DIR = os.path.dirname(__file__)
VCR = vcr.VCR(path_transformer=vcr.VCR.ensure_suffix('.yaml'),
              cassette_library_dir=os.path.join(
                  "tests", "cassetes", "data_cleaner"),
              record_mode='once')


def get_input(case_name):
    """Retorna el path al csv que se debe limpiar."""
    file_name = "to_clean_" + case_name + ".csv"
    return os.path.join(os.path.join(BASE_DIR, "input"), file_name)


def get_output(case_name):
    """Retorna el path al csv limpio que se espera."""
    file_name = "clean_" + case_name + ".csv"
    return os.path.join(os.path.join(BASE_DIR, "output"), file_name)


def nan_safe_list(iterable):
    """Retorna una lista convirtiendo valores nulos a None."""
    safe_list = []
    for element in iterable:
        if pd.isnull(element):
            safe_list.append(None)
        elif isinstance(element, six.string_types):
            if element == "None":
                safe_list.append(None)
            else:
                safe_list.append(element)
        else:
            safe_list.append(six.text_type(int(element)))

    return safe_list


def nan_to_empty_string_list(iterable):
    """Retorna una lista convirtiendo valores nulos a None."""
    return [i if pd.notnull(i) else "" for i in iterable]


def raw_csv(file_path):
    with open(file_path, 'r') as csvfile:
        return [row for row in csv.reader(csvfile)]


# @unittest.skip("skip")
class DataCleanerIntegrationTestCase(unittest.TestCase):
    """Testea el funcionamiento integral del paquete."""

    def test_integration_case_1(self):
        dc = DataCleaner(get_input("integration"))
        dc.clean_file(rules, get_output("temp_integration"))

        df = pd.read_csv(get_output("temp_integration"))
        df_exp = pd.read_csv(get_output("integration"))

        self.assertEqual(set(df.columns), set(df_exp.columns))
        for col in df.columns:
            self.assertEqual(
                nan_safe_list(df[col]), nan_safe_list(df_exp[col])
            )


class DataCleanerShapefileConversionTestCase(unittest.TestCase):
    """Testea la conversión de archivos Shapefile a otros formatos."""
    input_path = BASE_DIR + '/input/localidades/localidades.shp'

    def test_shapefile_to_csv(self):
        output_path = BASE_DIR + '/output/localidades.csv'

        dc = DataCleaner(self.input_path)
        dc.save(output_path)

        csv_df = pd.read_csv(output_path)
        self.assertEqual(set(csv_df.columns), set(dc.df.columns))

    @unittest.skip("skip")
    def test_shapefile_to_geojson(self):
        output_path = BASE_DIR + '/output/localidades.geojson'

        dc = DataCleaner(self.input_path)
        dc.save(output_path)

        geojson_df = gpd.read_file(output_path, driver='GeoJSON')
        self.assertEqual(set(geojson_df.columns), set(dc.df.columns))

    # Se saltea por error al ejecutar la conversión a KML.
    # _save_to_kml usa subprocess.call y corre localmente pero no en Travis-CI.
    @unittest.skip("skip")
    def test_shapefile_to_kml(self):
        output_path = BASE_DIR + '/output/localidades.kml'

        dc = DataCleaner(self.input_path)
        dc.save(output_path)

        with open(output_path) as kml_file:
            kml = kml_file.read()
            assert kml.startswith('<?xml version="1.0" encoding="utf-8" ?>')


class DataCleanerSingleMethodsTestCase(unittest.TestCase):
    """Testea métodos individuales de limpieza del DataCleaner."""

    def test_get_encoding(self):
        input_path = BASE_DIR + '/input/non_unicode.csv'

        dc = DataCleaner(input_path)
        encoding = dc._get_file_encoding(input_path)

        self.assertNotEqual(encoding, 'utf-8')

    def test_cleaning_fields(self):
        input_path = get_input("fields")
        output_path = get_output("fields")

        dc = DataCleaner(input_path)
        df = pd.read_csv(output_path, encoding="utf-8")

        self.assertEqual(set(dc.df.columns), set(df.columns))

    def test_removing_line_breaks(self):
        input_path = get_input("with_line_breaks")
        output_path = get_output("with_line_breaks")

        dc = DataCleaner(input_path)
        df = pd.read_csv(output_path, encoding="utf-8")

        self.assertEqual(list(dc.df.columna), list(df.columna))

    def test_repeated_fields(self):
        input_path = get_input("repeated_fields")

        with self.assertRaises(DuplicatedField):
            DataCleaner(input_path)

    def test_remover_columnas(self):
        input_path = get_input("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        df = dc.remover_columnas(field)

        self.assertNotIn(field, df.columns)

    def test_renombrar_columnas(self):
        input_path = get_input("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        df = dc.renombrar_columnas(field, "dependencia2")

        self.assertNotIn(field, df.columns)
        self.assertIn("dependencia2", df.columns)

    def test_renombrar_columnas_con_errores(self):
        input_path = get_input("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        df = dc.renombrar_columnas(field, " dependencia2")

        self.assertNotIn(field, df.columns)
        self.assertIn("dependencia2", df.columns)

    def test_nombre_propio(self):
        input_path = get_input("nombre_propio")
        output_path = get_output("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.nombre_propio(field)
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_nombre_propio_keep_original(self):
        input_path = get_input("nombre_propio")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        dc.nombre_propio(field, keep_original=True, inplace=True)

        self.assertIn("dependencia_normalizado", dc.df.columns)

    def test_nombre_propio_lower_words(self):
        input_path = get_input("nombre_propio")
        output_path = get_output("nombre_propio_lower_words")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.nombre_propio(
            field, lower_words=["nación", "de", "la"],
            keep_original=True, inplace=True)
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    # @unittest.skip("skip")
    def test_string_normal(self):
        input_path = get_input("string_normal")
        output_path = get_output("string_normal")
        field = "lugar_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.string(field)
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_mail_format(self):
        input_path = get_input("mail_format")
        output_path = get_output("mail_format")
        field = "mail"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.mail_format(field)
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_reemplazar(self):
        input_path = get_input("reemplazar")
        output_path = get_output("reemplazar")
        field = "tipo"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.reemplazar(field, {"Servicios": ["Serv"],
                                       "Otros": ["Otro", "Loc"]})
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_reemplazar_string(self):
        input_path = get_input("reemplazar_string")
        output_path = get_output("reemplazar_string")
        field = "dependencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.reemplazar_string(field, {"Jaguarete":
                                              ["ABBA", "ABBBA"]})
        res = list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = list(df[field])

        self.assertEqual(res, exp)

    def test_fecha_completa(self):
        input_path = get_input("fecha_completa")
        output_path = get_output("fecha_completa")
        field = "fecha_completa_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_completa(field, "DD-MM-YYYY HH:mm")
        res = nan_to_empty_string_list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = nan_to_empty_string_list(df["isodatetime_" + field])

        self.assertEqual(res, exp)

    def test_fecha_completa_keep_original(self):
        input_path = get_input("fecha_completa")
        field = "fecha_completa_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        dc.fecha_completa(field, "DD-MM-YYYY HH:mm",
                          keep_original=True, inplace=True)

        self.assertIn("isodatetime_fecha_completa_audiencia", dc.df.columns)

    def test_fecha_simple_sin_hora(self):
        input_path = get_input("fecha_sin_hora")
        output_path = get_output("fecha_sin_hora")
        field = "fecha_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_simple(field, "DD-MM-YYYY")
        res = nan_to_empty_string_list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = nan_to_empty_string_list(df["isodate_" + field])

        self.assertEqual(res, exp)

    def test_fecha_simple_mes(self):
        input_path = get_input("fecha_mes")
        output_path = get_output("fecha_mes")
        field = "fecha_audiencia"

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_simple(field, "MM-YYYY")
        res = nan_to_empty_string_list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = nan_to_empty_string_list(df["isodate_" + field])

        self.assertEqual(res, exp)

    def test_fecha_separada(self):
        input_path = get_input("fecha_separada")
        output_path = get_output("fecha_separada")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.fecha_separada([
            ["fecha_audiencia", "DD-MM-YYYY"],
            ["hora_audiencia", "HH:mm"]
        ],
            "audiencia")
        res = nan_to_empty_string_list(series)

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp = nan_to_empty_string_list(df["isodatetime_audiencia"])

        self.assertEqual(res, exp)

    def test_string_simple_split(self):
        input_path = get_input("string_separable_simple")
        output_path = get_output("string_separable_simple")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        parsed_df = dc.string_simple_split(
            "sujeto_obligado",
            [", Cargo:", "Cargo:"],
            ["nombre", "cargo"]
        )
        res_1 = nan_safe_list(parsed_df["sujeto_obligado_nombre"])
        res_2 = nan_safe_list(parsed_df["sujeto_obligado_cargo"])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp_1 = nan_safe_list(df["sujeto_obligado_nombre"])
        exp_2 = nan_safe_list(df["sujeto_obligado_cargo"])

        self.assertEqual(res_1, exp_1)
        self.assertEqual(res_2, exp_2)

    @unittest.skip("skip")
    def test_string_regex_split(self):
        pass

    # @unittest.skip("skip")
    def test_string_peg_split(self):
        input_path = get_input("string_separable_complejo")
        output_path = get_output("string_separable_complejo")

        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        parsed_df = dc.string_peg_split(
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
        res_1 = nan_safe_list(parsed_df["solicitante_nombre"])
        res_2 = nan_safe_list(parsed_df["solicitante_cargo"])
        res_3 = nan_safe_list(parsed_df["solicitante_dni"])

        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        exp_1 = nan_safe_list(df["solicitante_nombre"])
        exp_2 = nan_safe_list(df["solicitante_cargo"])
        exp_3 = nan_safe_list(df["solicitante_dni"])

        self.assertEqual(res_1, exp_1)
        self.assertEqual(res_2, exp_2)
        self.assertEqual(res_3, exp_3)

    def test_string_regex_substitute(self):
        input_path = get_input("regex_sub")
        output_path = get_output("regex_sub")
        # obtengo el resultado de limpiar el csv
        dc = DataCleaner(input_path)
        series = dc.string_regex_substitute("lugar_audiencia",
                                            "\d+.*$",
                                            "")
        res = list(series)
        # cargo el csv limpio para comparar
        df = pd.read_csv(output_path, encoding="utf-8")
        print(series)
        exp = list(df["lugar_audiencia"])
        self.assertEqual(res, exp)

    def test_simplify_geometry(self):
        input_path = BASE_DIR + '/input/localidades/localidades.shp'
        original = BASE_DIR + '/output/localidades-original.csv'
        simplified = BASE_DIR + '/output/localidades-simplificado.csv'

        dc = DataCleaner(input_path)
        dc.save(original)  # CSV con geometría original.
        dc = DataCleaner(input_path)
        dc.simplificar_geometria()
        dc.save(simplified)  # CSV con geometría simplificada.

        import filecmp
        files_are_equal = filecmp.cmp(original, simplified, shallow=False)
        self.assertFalse(files_are_equal)

    def test_simplify_non_geodataframe_object(self):
        # Genera un DataFrame sin geometría, para producir un error de tipo.
        input_path = get_input("nombre_propio")
        dc = DataCleaner(input_path)
        # simplificar_geometria() opera con objetos GeoDataFrame.
        nose.tools.assert_raises(TypeError, dc.simplificar_geometria)


class NormalizarUnidadTerritorialTestCase(unittest.TestCase):

    def test_invalidate_filters(self):
        """Debería encontrar filtros ínvalidos."""
        entity = 'departamento'
        test_filters = {
            "provincia_field": "provincia",
            "departamento_field": "provincia"
        }
        self.assertFalse(DataCleaner._validate_filters(entity, test_filters))

    def test_validate_filters(self):
        """Debería validar los filtros."""
        entity = 'localidad'
        test_filters = {
            "provincia_field": "provincia",
            "departamento_field": "departamento",
            "municipio_field": "municipio",
        }
        self.assertTrue(DataCleaner._validate_filters(entity, test_filters))

    def test_parsed_entity_level(self):
        """Pluraliza una unidad territorial."""
        test_string = [
            ("provincia", "provincias"),
            ("departamento", "departamentos"),
            ("municipio", "municipios"),
            ("localidad", "localidades")
        ]
        for (inp, outp) in test_string:
            self.assertEqual(DataCleaner._plural_entity_level(inp), outp)

    def test_build_data(self):
        """Construye un diccionario con unidades territoriales."""
        entity = str('localidad')
        field = str('nombre')
        test_data = {'localidades': [
            {'nombre': 'laferrere', 'aplanar': True, 'max': 1}
        ]}

        input_path = get_input('normalize_unidad_territorial')
        dc = DataCleaner(input_path)
        data = dc._build_data(field, entity, filters={})
        self.assertEqual(data, test_data)

    @VCR.use_cassette()
    def test_get_api_response(self):
        """Realiza un búsquedas sobre una entidad territorial."""
        entity = 'localidad'
        data_test = {'localidades': [
            {'nombre': 'laferrere', 'aplanar': True,
             'provincia': 'buenos aires', 'max': 1}
        ]}
        res_test = [
            {'localidades': [
                {u'departamento_nombre': u'La Matanza',
                 u'tipo': u'Entidad (E)',
                 u'centroide_lon': -58.592533,
                 u'municipio_nombre': u'La Matanza', u'provincia_id': u'06',
                 u'departamento_id': u'06427', u'id': u'06427010004',
                 u'centroide_lat': -34.746838,
                 u'provincia_nombre': u'Buenos Aires',
                 u'nombre': u'GREGORIO DE LAFERRERE',
                 u'municipio_id': u'060427'}]
             }]

        input_path = get_input('normalize_unidad_territorial')
        dc = DataCleaner(input_path)
        res = dc._get_api_response(entity, data_test)
        print(res)
        self.assertEqual(res_test, res)


class DataCleanerDataIntegrityTestCase(unittest.TestCase):
    """Testea que la integridad de los datasets se mantenga."""
    input_path = BASE_DIR + '/input/to_clean_coordinates.csv'

    def test_float_integrity(self):
        output_path = BASE_DIR + '/output/clean_coordinates.csv'

        dc = DataCleaner(self.input_path)
        dc.clean_file([], output_path)

        raw_input = raw_csv(self.input_path)
        raw_output = raw_csv(output_path)
        self.assertEqual(raw_input, raw_output)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
