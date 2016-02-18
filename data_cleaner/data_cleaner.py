#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cleaner de csvs a partir de reglas de limpieza.

DataCleaner permite aplicar reglas de limpieza a csvs.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import os
import pandas as pd


class DataCleaner(object):
    """Limpia csvs a partir de reglas de limpieza."""

    def __init__(self, input_path):
        self.df = pd.read_csv(input_path)

    def clean_file(self, rules, output_path):
        pass

    def nombre_propio(self, field):
        """Regla para todos los nombres propios.

        Capitaliza los nombres de países, ciudades, personas, instituciones y
        similares.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def string(self, field):
        """Regla para todos los strings.

        Aplica un algoritimo de clustering para normalizar strings que son
        demasiado parecidos, sin pérdida de información.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def fecha_completa(self, field, time_format):
        """Regla para fechas completas que están en un sólo campo.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def fecha_separada(self, fields, new_field_name):
        """Regla para fechas completas que están separadas en varios campos.

        Args:
            field (str): Campo a limpiar
            new_field_name (str): Sufijo para agregar a "isodatetime_".

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def string_simple_split(self, field, separators, new_field_names):
        """Regla para separar un campo a partir de separadores simples.

        Args:
            field (str): Campo a limpiar
            separators (list): Strings separadores.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def string_regex_split(self, field, pattern, new_field_names):
        """Regla para separar un campo a partir de una expresión regular.

        Args:
            field (str): Campo a limpiar.
            pattern (str): Expresión regular.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def string_peg_split(self, field, grammar, new_field_names):
        """Regla para separar un campo a partir parsing expression grammars.

        Args:
            field (str): Campo a limpiar.
            grammar (str): Reglas para compilar una PEG.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass


def main():
    pass

if __name__ == '__main__':
    main()
