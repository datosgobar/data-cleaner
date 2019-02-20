#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cleaner de CSVs a partir de reglas de limpieza.

La clase DataCleaner permite limpiar archivos CSVs con datos a partir de la
aplicación de reglas de limpieza.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import pandas as pd
import geopandas as gpd
import pycrs
from dateutil import tz
import arrow
import parsley
from unidecode import unidecode
import unicodecsv
import cchardet
import warnings
import inspect
import re
import subprocess
from functools import partial
from future.utils import iteritems
import six

from .fingerprint_keyer import group_fingerprint_strings
from .fingerprint_keyer import get_best_replacements, replace_by_key
from .capitalizer import capitalize

from .georef_api import *


class DuplicatedField(ValueError):
    """Salta cuando hay un campo duplicado en el dataset."""

    def __init__(self, value):
        """Crea mensaje de error."""
        msg = "El campo '{}' está duplicado. Campos duplicados no permitidos."
        super(DuplicatedField, self).__init__(msg)


class DataCleaner(object):
    """Crea un objeto DataCleaner cargando un CSV en un DataFrame y expone
    reglas de limpieza para operar sobre las columnas del objeto y retornar un
    CSV limplio."""

    OUTPUT_ENCODING = str("utf-8")
    OUTPUT_SEPARATOR = str(",")
    OUTPUT_QUOTECHAR = str('"')
    INPUT_DEFAULT_ENCODING = str("utf-8")
    INPUT_DEFAULT_SEPARATOR = str(",")
    INPUT_DEFAULT_QUOTECHAR = str('"')
    DEFAULT_SUFIX = "normalizado"

    def __init__(self, input_path, ignore_dups=False, **kwargs):
        """Carga datos a limpiar en un DataFrame, normalizando sus columnas.

        Args:
            input_path (str): Ruta al archivo que se va a limpiar.
            ignore_dups (bool): Ignora los duplicados en colunas
            kwargs: Todos los argumentos que puede tomar `pandas.read_csv`
        """
        default_args = {
            'encoding': self._get_file_encoding(input_path),
            'sep': self.INPUT_DEFAULT_SEPARATOR,
            'quotechar': self.INPUT_DEFAULT_QUOTECHAR
        }
        default_args.update(kwargs)

        # chequea que no haya fields con nombre duplicado
        if not ignore_dups and input_path.endswith('.csv'):
            self._assert_no_duplicates(input_path,
                                       encoding=default_args['encoding'],
                                       sep=default_args['sep'],
                                       quotechar=default_args['quotechar'])

        # lee el SHP a limpiar
        if input_path.endswith('.shp'):
            self.df = gpd.read_file(
                input_path,
                encoding=default_args['encoding']
            )
            # lee la proyección del .prj, si puede
            try:
                projection_path = input_path.replace('.shp', '.prj')
                self.source_crs = pycrs.loader.from_file(
                    projection_path).to_proj4()
            except Exception as e:
                print(e)
                self.source_crs = self.df.crs

        # lee el CSV a limpiar
        elif input_path.endswith('.csv'):
            self.df = pd.read_csv(input_path, dtype=six.text_type, **default_args)

        # lee el XLSX a limpiar
        elif input_path.endswith('.xlsx'):
            self.df = pd.read_excel(input_path, engine="xlrd", **default_args)

        else:
            raise Exception(
                "{} no es un formato soportado.".format(
                    input_path.split(".")[-1]))

        # limpieza automática
        # normaliza los nombres de los campos
        self.df.columns = self._normalize_fields(self.df.columns)

        # remueve todos los saltos de línea
        if len(self.df) > 0:
            self.df = self.df.applymap(self._remove_line_breaks)

        # guarda PEGs compiladas para optimizar performance
        self.grammars = {}

    def _assert_no_duplicates(self, input_path, encoding, sep, quotechar):

        if input_path.endswith('.csv'):
            with open(input_path, 'rb') as csvfile:
                reader = unicodecsv.reader(csvfile,
                                           encoding=encoding,
                                           delimiter=sep,
                                           quotechar=quotechar)
                fields = next(reader, [])

                for col in fields:
                    if fields.count(col) > 1:
                        raise DuplicatedField(col)

        # TODO: Implementar chequeo de que no hay duplicados para XLSX
        elif input_path.endswith('.xlsx'):
            pass

    def _get_file_encoding(self, file_path):
        """Detecta la codificación de un archivo con cierto nivel de confianza
           y devuelve esta codificación o el valor por defecto.

        Args:
            file_path (str): Ruta del archivo.

        Returns:
            str: Codificación del archivo.
        """
        with open(file_path, 'rb') as f:
            info = cchardet.detect(f.read())
        return (info['encoding'] if info['confidence'] > 0.75
                else self.INPUT_DEFAULT_ENCODING)

    def _normalize_fields(self, fields):
        return [self._normalize_field(field) for field in fields]

    def _normalize_field(self, field, sep="_"):
        """Normaliza un string para ser nombre de campo o sufijo de dataset.

        Args:
            field (str): Nombre original del campo o sufijo de datset.
            sep (str): Separador para el nombre normalizado.

        Returns:
            str: Nombre de campo o sufijo de datset normalizado.
        """
        if not isinstance(field, six.string_types):
            field = six.text_type(field)

        # reemplaza caracteres que no sean unicode
        norm_field = unidecode(field).strip()

        norm_field = norm_field.replace(" ", sep)
        norm_field = norm_field.replace("-", sep).replace("_", sep)
        norm_field = norm_field.replace("/", sep)
        norm_field = self._camel_convert(norm_field).lower()

        # remueve caracteres que no sean alfanuméricos o "_"
        norm_field = ''.join(char for char in norm_field
                             if char.isalnum() or char == "_")

        # emite un Warning si tuvo que normalizar el field
        if field != norm_field:
            caller_rule = self._get_normalize_field_caller(
                inspect.currentframe())
            msg = """

El campo "{}" no sigue las convenciones para escribir
campos (sólo se admiten caracteres alfanuméricos ASCII en
minúsculas, con palabras separadas por "{}"). DataCleaner
normaliza automáticamente los campos en estos casos, lo
que puede llevar a resultados inesperados.

El nuevo nombre del campo normalizado es: "{}".
Método que llamó al normalizador de campos: {}
""".format(field, sep, norm_field, caller_rule)
            warnings.warn(msg)

        return norm_field

    @staticmethod
    def _camel_convert(name):
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)

    @staticmethod
    def _get_normalize_field_caller(curframe):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        if calframe[2][3] != "_normalize_fields":
            caller_rule = calframe[2][3]
        else:
            caller_rule = calframe[3][3]

        return caller_rule

    @staticmethod
    def _remove_line_breaks(value, replace_char=" "):
        if isinstance(value, six.string_types):
            return six.text_type(value).replace('\n', replace_char)
        else:
            return value

    # Métodos GLOBALES
    def clean(self, rules):
        """Aplica las reglas de limpieza al objeto en memoria.

        Args:
            rules (list): Lista de reglas de limpieza.
        """
        for rule_item in rules:
            for rule in rule_item:
                rule_method = getattr(self, rule)
                for kwargs in rule_item[rule]:
                    kwargs["inplace"] = True
                    rule_method(**kwargs)

    def clean_file(self, rules, output_path):
        """Aplica las reglas de limpieza y guarda los datos en un csv.

        Args:
            rules (list): Lista de reglas de limpieza.
        """
        self.clean(rules)
        self.save(output_path)

    def save(self, output_path, geometry_name='geojson',
             geometry_crs='epsg:4326'):
        """Guarda los datos en un nuevo CSV con formato estándar.

        El CSV se guarda codificado en UTF-8, separado con "," y usando '"'
        comillas dobles como caracter de enclosing."""

        if isinstance(self.df, gpd.GeoDataFrame):
            # Convierte la proyección, si puede.
            if geometry_crs:
                try:
                    self.df.crs = self.source_crs
                    self.df = self.df.to_crs({'init': geometry_crs})
                except Exception as e:
                    print(e)
                    print("Se procede sin re-proyectar las coordenadas.")

            if output_path.endswith('.csv'):
                self._set_json_geometry(geometry_name)

            # Guarda el archivo en formato GeoJSON o KML.
            if output_path.endswith('json'):  # Acepta .json y .geojson.
                self.df.to_file(output_path, driver='GeoJSON')
                return
            elif output_path.endswith('kml'):
                self._save_to_kml(output_path)
                return
        self.df.set_index(self.df.columns[0]).to_csv(
            output_path, encoding=self.OUTPUT_ENCODING,
            sep=self.OUTPUT_SEPARATOR,
            quotechar=self.OUTPUT_QUOTECHAR)

    def _save_to_kml(self, output_path):
        aux_file = output_path + '.json'
        self.df.to_file(aux_file, driver='GeoJSON')
        command = 'ogr2ogr -f KML {} {}'.format(output_path, aux_file)
        subprocess.call(command, shell=True)
        os.remove(aux_file)

    def _set_json_geometry(self, geometry_name):
        """Transforma la geometría del GeoDataFrame a formato JSON."""
        geojson = self.df.geometry.to_json()
        features = json.loads(geojson)['features']
        geometries = [feature['geometry'] for feature in features]
        # Convierte cada geometría en un string JSON válido.
        self.df[geometry_name] = [json.dumps(geometry)
                                  for geometry in geometries]
        del self.df['geometry']

    def _update_series(self, field, new_series,
                       keep_original=False, prefix=None, sufix=None):
        """Agrega o pisa una serie nueva en el DataFrame."""
        if not keep_original:
            self.df[field] = new_series
        else:
            new_field = "_".join([elem for elem in [prefix, field, sufix]
                                  if elem])
            self.df.insert(self.df.columns.get_loc(field),
                           new_field, new_series)

    # Métodos INDIVIDUALES de LIMPIEZA
    def remover_columnas(self, field, inplace=False):
        """Remueve columnas.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.DataFrame: Data frame con las columnas removidas.
        """
        field = self._normalize_field(field)
        if field not in self.df.columns:
            warnings.warn("No existe el campo '{}'".format(field))
            return self.df
        removed_df = self.df.drop(field, axis=1)

        if inplace:
            self.df = removed_df

        return removed_df

    def renombrar_columnas(self, field, new_field, inplace=False):
        """Renombra una columna.

        Args:
            field (str): Campo a renombrar.
            field (str): Nuevo nombre

        Returns:
            pandas.DataFrame: Data frame con las columnas renombradas.
        """
        field = self._normalize_field(field)
        new_field = self._normalize_field(new_field)
        renamed_df = self.df.rename(columns={field: new_field})

        if inplace:
            self.df = renamed_df

        return renamed_df

    def nombre_propio(self, field, sufix=None, lower_words=None,
                      keep_original=False, inplace=False):
        """Regla para todos los nombres propios.

        Capitaliza los nombres de países, ciudades, personas, instituciones y
        similares.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field]
        capitalized = series.apply(capitalize, lower_words=lower_words)

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=capitalized)
        return capitalized

    def string(self, field, sufix=None, sort_tokens=False,
               remove_duplicates=False, keep_original=False, inplace=False):
        """Regla para todos los strings.

        Aplica un algoritimo de clustering para normalizar strings que son
        demasiado parecidos, sin pérdida de información.

        Args:
            field (str): Campo a limpiar.

        Returns:
            pandas.Series: Serie de strings limpios.
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field]

        clusters, counts = group_fingerprint_strings(
            series, sort_tokens=sort_tokens,
            remove_duplicates=remove_duplicates)
        replacements = get_best_replacements(clusters, counts)
        parsed_series = pd.Series(replace_by_key(replacements, series))
        parsed_series = parsed_series.str.strip()

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=parsed_series)

        return parsed_series

    def mail_format(self, field, sufix=None,
                    keep_original=False, inplace=False):
        """Regla para dar formato a las direcciones de correo electronico.

        Lleva todas las cadenas a minusculas y luego si hay varias las separa
        por comas.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field].str.lower()
        series = series.str.findall('[a-z_0-9\.]+@[a-z_0-9\.]+').str.join(", ")

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=series)

        return series

    def reemplazar(self, field, replacements, sufix=None,
                   keep_original=False, inplace=False):
        """Reemplaza listas de valores por un nuevo valor.

        Args:
            field (str): Campo a limpiar
            replacements (dict): {"new_value": ["old_value1", "old_value2"]}

        Returns:
            pandas.Series: Serie de strings limpios
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field]

        for new_value, old_values in iteritems(replacements):
            series = series.replace(old_values, new_value)

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=series)

        return series

    def reemplazar_string(self, field, replacements, sufix=None,
                          keep_original=False, inplace=False):
        """Reemplaza listas de strings por un nuevo string.
           A diferencias de la funcion reemplazar hace reemplazos parciales.

        Args:
            field (str): Campo a limpiar
            replacements (dict): {"new_value": ["old_value1", "old_value2"]}

        Returns:
            pandas.Series: Serie de strings limpios
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field]

        for new_value, old_values in iteritems(replacements):
            # for old_value in sorted(old_values, key=len, reverse=True):
            for old_value in old_values:
                replace_function = partial(self._safe_replace,
                                           old_value=old_value,
                                           new_value=new_value)
                series = map(replace_function, series)

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=series)

        return series

    @staticmethod
    def _safe_replace(string, old_value, new_value):
        if pd.isnull(string):
            return pd.np.nan
        else:
            return six.text_type(string).replace(old_value, new_value)

    def fecha_completa(self, field, time_format, keep_original=False,
                       inplace=False):
        """Regla para fechas completas que están en un sólo campo.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        series = self.df[field]
        parsed_series = series.apply(self._parse_datetime,
                                     args=(time_format,))
        if inplace:
            self._update_series(field=field, prefix="isodatetime",
                                keep_original=keep_original,
                                new_series=parsed_series)

        return parsed_series

    def fecha_simple(self, field, time_format, keep_original=False,
                     inplace=False):
        """Regla para fechas sin hora, sin día o sin mes.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        series = self.df[field]
        parsed_series = series.apply(self._parse_date,
                                     args=(time_format,))

        if inplace:
            self._update_series(field=field, prefix="isodate",
                                keep_original=keep_original,
                                new_series=parsed_series)

        return parsed_series

    @staticmethod
    def _parse_datetime(value, time_format):
        try:
            datetime = arrow.get(
                value, time_format,
                tzinfo=tz.gettz("America/Argentina/Buenos Aires"), locale='es')
            return datetime.isoformat()
        except:
            return ""

    @staticmethod
    def _parse_date(value, time_format):
        try:
            datetime = arrow.get(
                value, time_format,
                tzinfo=tz.gettz("America/Argentina/Buenos Aires"))
            date = datetime.isoformat().split("T")[0]

            if "D" in time_format:
                return date
            elif "M" in time_format:
                return "-".join(date.split("-")[:-1])
            else:
                return "-".join(date.split("-")[:-2])
        except:
            return ""

    def fecha_separada(self, fields, new_field_name, keep_original=True,
                       inplace=False):
        """Regla para fechas completas que están separadas en varios campos.

        Args:
            field (str): Campo a limpiar.
            new_field_name (str): Sufijo para construir nombre del nuevo field.

        Returns:
            pandas.Series: Serie de strings limpios.
        """
        field_names = [self._normalize_field(field[0]) for field in fields]
        time_format = " ".join([field[1] for field in fields])

        concat_series = self.df[field_names].apply(
            lambda x: ' '.join(x.map(six.text_type)),
            axis=1
        )

        parsed_series = concat_series.apply(self._parse_datetime,
                                            args=(time_format,))

        if inplace:
            self.df["isodatetime_" + new_field_name] = parsed_series
            if not keep_original:
                for field in field_names:
                    self.remover_columnas(field)

        return parsed_series

    def string_simple_split(self, field, separators, new_field_names,
                            keep_original=True, inplace=False):
        """Regla para separar un campo a partir de separadores simples.

        Args:
            field (str): Campo a limpiar
            separators (list): Strings separadores.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        series = self.df[field]
        parsed_df = series.apply(self._split, args=(separators,))

        parsed_df.rename(
            columns={key: field + "_" + value
                     for key, value in enumerate(new_field_names)},
            inplace=True
        )

        if inplace:
            self.df = pd.concat([self.df, parsed_df], axis=1)
        if not keep_original:
            self.remover_columnas(field)

        return parsed_df

    @staticmethod
    def _split(value, separators):
        values = []
        for separator in separators:
            if separator in six.text_type(value):
                values = [six.text_type(split_value) for split_value in
                          value.split(separator)]
                break

        return pd.Series([six.text_type(value).strip() for value in values
                          if pd.notnull(value)])

    def string_regex_split(self, field, pattern, new_field_names,
                           keep_original=True, inplace=False):
        """Regla para separar un campo a partir de una expresión regular.

        TODO!!! Falta implementar este método.

        Args:
            field (str): Campo a limpiar.
            pattern (str): Expresión regular.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        pass

    def string_peg_split(self, field, grammar, new_field_names,
                         keep_original=True, inplace=False):
        """Regla para separar un campo a partir parsing expression grammars.

        Args:
            field (str): Campo a limpiar.
            grammar (str): Reglas para compilar una PEG.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        series = self.df[field]
        parsed_df = series.apply(self._split_with_peg, args=(grammar,))

        parsed_df.rename(
            columns={key: field + "_" + value
                     for key, value in enumerate(new_field_names)},
            inplace=True
        )

        if inplace:
            self.df = pd.concat([self.df, parsed_df], axis=1)
        if not keep_original:
            self.remover_columnas(field)

        return parsed_df

    def _split_with_peg(self, value, grammar):
        if grammar in self.grammars:
            comp_grammar = self.grammars[grammar]
        else:
            comp_grammar = parsley.makeGrammar(grammar, {})
            self.grammars[grammar] = comp_grammar

        try:
            values = comp_grammar(value).values()
        except:
            values = []

        values = [six.text_type(split_value) for split_value in values]

        return pd.Series(values)

    def string_regex_substitute(self, field, regex_str_match,
                                regex_str_sub, sufix=None,
                                keep_original=True, inplace=False):
        """Regla para manipular y reeemplazar datos de un campo con regex.

        Args:
            field (str): Campo a limpiar.
            regex_str_match (str): Expresion regular a buscar
            regex_str_sub (str): Expresion regular para el reemplazo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        sufix = sufix or self.DEFAULT_SUFIX
        field = self._normalize_field(field)
        series = self.df[field]
        replaced = series.str.replace(regex_str_match, regex_str_sub)

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=replaced)

        return replaced

    def simplificar_geometria(self, tolerance=0.5,
                              keep_original=True, inplace=False):
        """Simplifica una geometría para que resulte
           en un objeto de menor tamaño y complejidad,
           que a la vez retenga sus características esenciales.

        Args:
            tolerance (float): Nivel de tolerancia en la transformación.

        Returns:
            pandas.Series: Serie de geometrías.
        """
        if isinstance(self.df, gpd.GeoDataFrame):
            self.df.geometry = self.df.geometry.simplify(tolerance)
            return self.df.geometry
        else:
            raise TypeError('El dataframe no es de tipo GeoDataFrame.')

    def normalizar_unidad_territorial(self, field, entity_level, add_code=False,
                                      add_centroid=False, add_parents=None,
                                      filters=None, keep_original=False,
                                      inplace=False):
        """Normaliza y enriquece una unidad territorial del DataFrame.

        Args:
            field (str): Nombre del campo a normalizar.
            entity_level (str): Nivel de la unidad territorial.
            add_code (bool): Específica si agrega código de la entidad.
            add_centroid (bool): Específica si agrega centroide de la entidad.
            add_parents (list): Lista de entidades padres a agregar.
            filters (dict): Diccionario con entidades por las cuales filtrar.
            keep_original (bool): Específica si conserva la columna original.
            inplace (bool): Específica si la limpieza perdura en el objeto.

        Returns:
            pandas.Series: Serie de unidades territoriales normalizadas y
                limpias.
        """
        if len(self.df) > 100000:
            print('El número máximo de unidades a normalizar es de 100000.')
            return

        if not self._validate_entity_level(entity_level):
            print('"{}" no es un nivel de entidad válido.'.format(entity_level))
            return

        if filters:
            if not self._validate_filters(entity_level, filters):
                return self.df

        data = self._build_data(field, entity_level, filters)
        if data:
            res = self._get_api_response(entity_level, data)

            if 'error' in res:
                print(res['error'])

            if keep_original:
                field_normalized = six.text_type(field + '_normalized')
                self._update_column(field_normalized, NAME, entity_level, res)
            else:
                self._update_column(field, NAME, entity_level, res)

            if add_code:
                column_code = entity_level + '_' + ID
                self._update_column(column_code, ID, entity_level, res)

            if add_centroid:
                column_lat = entity_level + '_' + LAT
                column_lon = entity_level + '_' + LON
                self._update_column(column_lat, LAT, entity_level, res)
                self._update_column(column_lon, LON, entity_level, res)

            if add_parents:
                for parent in add_parents:
                    if entity_level not in PROV and parent in PROV:
                        self._update_column(PROV_ID, PROV_ID, entity_level, res)
                        self._update_column(PROV_NAM, PROV_NAM, entity_level,
                                            res)
                    if parent in DEPT and entity_level in [MUN, LOC]:
                        self._update_column(DEPT_ID, DEPT_ID, entity_level, res)
                        self._update_column(DEPT_NAM, DEPT_NAM, entity_level,
                                            res)
                    if parent in MUN and entity_level in LOC:
                        self._update_column(MUN_ID, MUN_ID, entity_level, res)
                        self._update_column(MUN_NAM, MUN_NAM, entity_level, res)

            return self.df
        else:
            return

    @staticmethod
    def _validate_filters(entity_level, filters):
        """Verifica que los filtros sean validos con el nivel de entidad a
        normalizar.

        Args:
            entity_level: Nivel de la unidad territorial por la cual filtrar.
            filters (dict): Diccionario con filtros.

        Returns:
            bool: Verdadero si los filtros son válidos.
        """

        field_prov = PROV + '_field'
        field_dept = DEPT + '_field'
        field_mun = MUN + '_field'

        # Verfica que se utilicen keywords válidos por entidad
        for key, value in iteritems(filters):

            if key not in [field_prov, field_dept, field_mun]:
                print('"{}" no es un keyword válido.'.format(key))
                return
            if entity_level in key or entity_level in PROV:
                print('"{}" no es un filtro válido para la entidad "{}."'
                      .format(key, entity_level))
                return
            if entity_level in DEPT and PROV not in key:
                print('"{}" no es un filtro válido para la entidad "{}".'
                      .format(key, entity_level))
                return

        return True

    def _build_data(self, field, entity_level, filters):
        """Construye un diccionario con una lista de unidades territoriales
        para realizar consultas a la API de normalización Georef utilizando
        el método bulk.

        Args:
            field (str): Nombre del campo a normalizar.
            entity_level (str): Nivel de la unidad territorial.
            filters (dict): Diccionario con entidades por las cuales filtrar.

        Returns:
            dict: (dict): Diccionario a utilizar para realizar una consulta.
            En caso de error devuelve False.
        """
        body = []
        entity_level = self._plural_entity_level(entity_level)

        try:
            for item, row in self.df.iterrows():
                row = row.fillna('0')  # reemplaza valores 'nan' por '0'
                data = {'nombre': row[field], 'max': 1, 'aplanar': True}

                if filters:
                    filters_builded = self._build_filters(row, filters)
                    data.update(filters_builded)
                body.append(data)

            return {entity_level: body}
        except KeyError as e:
            print('Error: No existe el campo "{}".'.format(e))
        except Exception as e:
            print(e)
        return False

    @staticmethod
    def _build_filters(row, filters):
        """Contruye un diccionario con filtros de unidades territoriales.

        Args:
            row (pandas.Series): Serie con strings de unidades territoriales.
            filters (dict): Diccionario con filtros.

        Returns:
            params (dict): Diccionario con filtros.
        """

        params = {}
        field_prov = PROV + '_field'
        field_dept = DEPT + '_field'
        field_mun = MUN + '_field'
        row = row.fillna(0)

        # Si existe el filtro y su valor no es 0 lo agrega al diccionario
        if field_prov in filters and row[filters[field_prov]]:
                params.update({PROV: row[filters[field_prov]]})
        if field_dept in filters and row[filters[field_dept]]:
                params.update({DEPT: row[filters[field_dept]]})
        if field_mun in filters and row[filters[field_mun]]:
                params.update({MUN: row[filters[field_mun]]})
        return params

    @staticmethod
    def _get_api_response(entity_level, data):
        """Realiza búsquedas sobre un listado de entidades en simultáneo
        utilizando el método bulk de la API de normalización Georef.

        Args:
            entity_level (str): Nivel de la unidad territorial a consultar.
            data (dict): Diccionario que contiene un listado de unidades
                territoriales.

        Returns:
            results (list): Lista con resultados de la búsqueda.
        """
        wrapper = GeorefWrapper()
        if entity_level in PROV:
            results = wrapper.search_province(data)
        elif entity_level in DEPT:
            results = wrapper.search_departament(data)
        elif entity_level in MUN:
            results = wrapper.search_municipality(data)
        else:
            results = wrapper.search_locality(data)
        return results

    def _update_column(self, column, attribute, entity_level, results):
        """Actualiza una columna específica del DataFrame.

        Args:
            column (str): Nombre de la columna a agregar y/o actualizar.
            attribute (str): Nombre del atributo del
            entity_level (str): Nivel de la unidad territorial a consultar.
            results (list): Resultado de la consulta a la API.

        Return:
            None
        """
        entity_level = self._plural_entity_level(entity_level)

        if column not in self.df:
            self.df[column] = None

        idx = 0
        for row in results:
            if row[entity_level]:
                self.df.loc[idx, column] = row[entity_level][0][attribute]
            idx += 1

    @staticmethod
    def _plural_entity_level(entity_level):
        """Pluraliza el nombre de una unidad territorial.

        Args:
            entity_level (str): Nivel de la unidad territorial a pluralizar.

        Return:
            entity_level (str): Nombre pluralizado.
        """
        if LOC not in entity_level:
            entity_level = entity_level + 's'
        else:
            entity_level = entity_level + 'es'
        return entity_level

    @staticmethod
    def _validate_entity_level(entity_level):
        """Válida el nivel de la unidad territorial.

        Args:
            entity_level (str): Nivel de la unidad territorial a validar.

        Return:
            bool: Verdadero si es un nivel de entidad válida.
        """
        if entity_level in [PROV, DEPT, MUN, LOC]:
            return True
        return False
