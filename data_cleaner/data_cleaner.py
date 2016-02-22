#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cleaner de csvs a partir de reglas de limpieza.

DataCleaner permite aplicar reglas de limpieza a csvs.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import pandas as pd
from dateutil import tz
import arrow
import parsley
from unidecode import unidecode

from fingerprint_keyer import group_fingerprint_strings
from fingerprint_keyer import get_best_replacements, replace_by_key


class DataCleaner(object):
    """Limpia csvs a partir de reglas de limpieza."""

    OUTPUT_ENCODING = str("utf-8")
    OUTPUT_SEPARATOR = str(",")
    OUTPUT_QUOTECHAR = str('"')
    INPUT_DEFAULT_ENCODING = str("utf-8")
    INPUT_DEFAULT_SEPARATOR = str(",")
    INPUT_DEFAULT_QUOTECHAR = str('"')

    NO_ARGS_RULES = ["nombre_propio", "string", "remover_columnas"]

    def __init__(self, input_path, encoding=None, sep=None, quotechar=None):
        """Carga un CSV a limpiar en un DataFrame, normalizando sus columnas.

        Args:
            input_path (str): Ruta al CSV que se va a limpiar.
            encoding (str): Encoding del CSV a limpiar (default: utf-8)
            sep (str): Separador del CSV a limpiar (default: ",")
            quotechar (str): Enclosing character del CSV (default: '"')
        """
        self.encoding = encoding or self.INPUT_DEFAULT_ENCODING
        sep = sep or self.INPUT_DEFAULT_SEPARATOR
        quotechar = quotechar or self.INPUT_DEFAULT_QUOTECHAR

        self.df = pd.read_csv(input_path, encoding=encoding, sep=sep,
                              quotechar=quotechar)
        self.df.columns = self._normalize_fields(self.df.columns)

        self.grammars = {}

        self.save.__func__.__doc__ = pd.DataFrame.to_csv.__func__.__doc__

    def _normalize_fields(self, fields):
        return [self._normalize_field(field) for field in fields]

    def _normalize_field(self, field):
        # reemplaza caracteres que no sean unicode
        norm_field = unidecode(field.decode(self.encoding))

        norm_field = norm_field.lower().replace(" ", "_").replace("-", "_")

        # remueve caracteres que no sean alfanuméricos o "_"
        norm_field = ''.join(char for char in norm_field
                             if char.isalnum() or char == "_")
        return norm_field

    # Métodos GLOBALES
    def clean(self, rules):
        """Aplica las reglas de limpieza al objeto en memoria.

        Args:
            rules (list): Lista de reglas de limpieza.
        """
        for rule_item in rules:
            for rule in rule_item:
                rule_method = getattr(self, rule)

                if rule in self.NO_ARGS_RULES:
                    fields = rule_item[rule]
                    for field in fields:
                        rule_method(field, inplace=True)

                else:
                    for args in rule_item[rule]:
                        rule_method(*args, inplace=True)

    def clean_file(self, rules, output_path):
        """Aplica las reglas de limpieza y guarda los datos en un csv.

        Args:
            rules (list): Lista de reglas de limpieza.
        """
        self.clean(rules)
        self.save(output_path, encoding=self.OUTPUT_ENCODING,
                  separator=self.OUTPUT_SEPARATOR,
                  quotechar=self.OUTPUT_QUOTECHAR)

    def save(self, output_path, *args, **kwargs):
        """Redirige al método DataFrame.to_csv()."""
        self.df.set_index(self.df.columns[0]).to_csv(
            output_path, *args, **kwargs)

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

    def nombre_propio(self, field, inplace=False):
        """Regla para todos los nombres propios.

        Capitaliza los nombres de países, ciudades, personas, instituciones y
        similares.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)
        capitalized = decoded_series.str.title()
        encoded_series = capitalized.str.encode(self.OUTPUT_ENCODING)

        if inplace:
            self.df[field] = encoded_series

        return encoded_series

    def string(self, field, inplace=False):
        """Regla para todos los strings.

        Aplica un algoritimo de clustering para normalizar strings que son
        demasiado parecidos, sin pérdida de información.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)

        clusters, counts = group_fingerprint_strings(decoded_series)
        d = get_best_replacements(clusters, counts)
        parsed_series = pd.Series(replace_by_key(d, decoded_series))
        encoded_series = parsed_series.str.encode(self.OUTPUT_ENCODING)

        if inplace:
            self.df[field] = encoded_series

        return encoded_series

    def reemplazar(self, field, values_map, inplace=False):
        """Reemplaza listas de valores por un nuevo valor.

        Args:
            field (str): Campo a limpiar
            values_map (dict): {"new_value": ["old_value1", "old_value2"]}

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)

        for new_value, old_values in values_map.iteritems():
            decoded_series = decoded_series.replace(old_values, new_value)

        encoded_series = decoded_series.str.encode(self.OUTPUT_ENCODING)

        if inplace:
            self.df[field] = encoded_series

        return encoded_series

    def fecha_completa(self, field, time_format, inplace=False):
        """Regla para fechas completas que están en un sólo campo.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)
        parsed_series = decoded_series.apply(self._parse_datetime,
                                             args=(time_format,))
        if inplace:
            self.df["isodatetime_" + field] = parsed_series

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

    def fecha_simple(self, field, time_format, inplace=False):
        """Regla para fechas sin hora, sin día o sin mes.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)
        parsed_series = decoded_series.apply(self._parse_date,
                                             args=(time_format,))
        if inplace:
            self.df["isodate_" + field] = parsed_series

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

    @staticmethod
    def _parse_datetime(value, time_format):
        try:
            datetime = arrow.get(
                value, time_format,
                tzinfo=tz.gettz("America/Argentina/Buenos Aires"))
            return datetime.isoformat()
        except:
            return pd.np.NaN

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
            return pd.np.NaN

    def fecha_separada(self, fields, new_field_name, inplace=False):
        """Regla para fechas completas que están separadas en varios campos.

        Args:
            field (str): Campo a limpiar
            new_field_name (str): Sufijo para agregar a "isodatetime_".

        Returns:
            pandas.Series: Serie de strings limpios
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

        return parsed_series.str.encode(self.OUTPUT_ENCODING)

    def string_simple_split(self, field, separators, new_field_names,
                            inplace=False):
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
        decoded_series = self.df[field].str.decode(self.encoding)
        parsed_df = decoded_series.apply(self._split, args=(separators,))
        parsed_df.rename(
            columns={key: field + "_" + value
                     for key, value in enumerate(new_field_names)},
            inplace=True
        )

        if inplace:
            self.df = pd.concat([self.df, parsed_df], axis=1)

        return parsed_df

    @staticmethod
    def _split(value, separators):
        values = []
        for separator in separators:
            if separator in str(value):
                values = value.split(separator)
                break

        return pd.Series([str(value).strip() for value in values
                          if pd.notnull(value)])

    def string_regex_split(self, field, pattern, new_field_names,
                           inplace=False):
        """Regla para separar un campo a partir de una expresión regular.

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

    def string_peg_split(self, field, grammar, new_field_names, inplace=False):
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
        decoded_series = self.df[field].str.decode(self.encoding)
        parsed_df = decoded_series.apply(self._split_with_peg, args=(grammar,))
        parsed_df.rename(
            columns={key: field + "_" + value
                     for key, value in enumerate(new_field_names)},
            inplace=True
        )

        if inplace:
            self.df = pd.concat([self.df, parsed_df], axis=1)

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

        return pd.Series(values)

    def string_regex_substitute(self, field, regex_str_match,
                                regex_str_sub, inplace=False):
        """Regla para manipular y reeemplazar datos de un campo con regex.

        Args:
            field (str): Campo a limpiar.
            regex_str_match (str): Expresion regular a buscar
            regex_str_sub (str): Expresion regular para el reemplazo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field = self._normalize_field(field)
        decoded_series = self.df[field].str.decode(self.encoding)
        replaced = decoded_series.replace(regex_str_match,
                                          regex_str_sub, regex=True)
        encoded_series = replaced.str.encode(self.OUTPUT_ENCODING)

        if inplace:
            self.df[field] = encoded_series

        return encoded_series


def main():
    pass

if __name__ == '__main__':
    main()
