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
from dateutil import tz
import arrow
import parsley
from unidecode import unidecode
import unicodecsv
import warnings
import inspect
import re
from functools import partial

from fingerprint_keyer import group_fingerprint_strings
from fingerprint_keyer import get_best_replacements, replace_by_key
from capitalizer import capitalize


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

    def __init__(self, input_path, encoding=None, sep=None, ignore_dups=False,
                 quotechar=None):
        """Carga un CSV a limpiar en un DataFrame, normalizando sus columnas.

        Args:
            input_path (str): Ruta al CSV que se va a limpiar.
            encoding (str): Encoding del CSV a limpiar (default: utf-8)
            sep (str): Separador del CSV a limpiar (default: ",")
            quotechar (str): Enclosing character del CSV (default: '"')
        """
        encoding = encoding or self.INPUT_DEFAULT_ENCODING
        sep = sep or self.INPUT_DEFAULT_SEPARATOR
        quotechar = quotechar or self.INPUT_DEFAULT_QUOTECHAR

        # chequea que no haya fields con nombre duplicado
        if not ignore_dups:
            self._assert_no_duplicates(input_path, encoding=encoding, sep=sep,
                                       quotechar=quotechar)

        # lee el CSV a limpiar
        self.df = pd.read_csv(input_path, encoding=encoding, sep=sep,
                              quotechar=quotechar)

        # limpieza automática
        # normaliza los nombres de los campos
        self.df.columns = self._normalize_fields(self.df.columns)

        # remueve todos los saltos de línea
        if len(self.df) > 0:
            self.df = self.df.applymap(self._remove_line_breaks)

        # guarda PEGs compiladas para optimizar performance
        self.grammars = {}

        self.save.__func__.__doc__ = pd.DataFrame.to_csv.__func__.__doc__

    def _assert_no_duplicates(self, csv_path, encoding, sep, quotechar):
        with open(csv_path, 'r') as csvfile:
            reader = unicodecsv.reader(csvfile,
                                       encoding=encoding,
                                       delimiter=sep,
                                       quotechar=quotechar)
            fields = reader.next()

            for col in fields:
                if fields.count(col) > 1:
                    raise DuplicatedField(col)

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
        if type(field) is not str and type(field) is not unicode:
            field = unicode(field)

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
""".format(field, sep, norm_field, caller_rule).encode("utf-8")
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
        if type(value) == unicode or type(value) == str:
            return value.replace("\n", replace_char)
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

    def save(self, output_path):
        """Guarda los datos en un nuevo CSV con formato estándar.

        El CSV se guarda codificado en UTF-8, separado con "," y usando '"'
        comillas dobles como caracter de enclosing."""

        self.df.set_index(self.df.columns[0]).to_csv(
            output_path, encoding=self.OUTPUT_ENCODING,
            separator=self.OUTPUT_SEPARATOR,
            quotechar=self.OUTPUT_QUOTECHAR)

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

        for new_value, old_values in replacements.iteritems():
            series = series.replace(old_values, new_value)

        encoded_series = series.str.encode(self.OUTPUT_ENCODING)

        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=encoded_series)

        return encoded_series

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

        for new_value, old_values in replacements.iteritems():
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
            return unicode(string).replace(old_value, new_value)

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

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

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

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

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
            lambda x: ' '.join(x.map(str)),
            axis=1
        )

        parsed_series = concat_series.apply(self._parse_datetime,
                                            args=(time_format,))

        if inplace:
            self.df["isodatetime_" + new_field_name] = parsed_series
            if not keep_original:
                for field in field_names:
                    self.remover_columnas(field)

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

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
            if separator in unicode(value):
                values = [unicode(split_value) for split_value in
                          value.split(separator)]
                break

        return pd.Series([unicode(value).strip() for value in values
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

        values = [unicode(split_value) for split_value in values]

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
