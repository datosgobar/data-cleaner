#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Template de script de limpieza usando DataCleaner

Utiliza el paquete `data-cleaner` para limpiar datos de un CSV aplicando:
    * Reglas de limpieza disponibles en el paquete
    * Reglas de limpieza creadas sobre el objeto extendido MyDataCleaner
    * Cualquier script de limpieza custom que deba aplicarse antes o después de
        las reglas.

Cuando usar custom scripts:
    El usuario tiene que aplicar tareas muy específicas del dataset a limpiar,
    que dificilmente podrían ser reutilizadas para extender `data-cleaner`.
    Como por ejemplo un filtro / recorte global antes o después de la limpieza.

Cuando extender la clase MyDataCleaner con una nueva regla:
    El usuario necesita utilizar una regla de limpieza que no está disponible,
    pero puede ser pensada para un caso general que abarque distintos tipos de
    uso. Implementarla siguiendo la interfaz del DataCleaner permite tener el
    nuevo método listo para integrar al paquete más adelante.

Uso desde la línea de comandos:
    python cleaning_script.py
    python cleaning_script.py input_path
    python cleaning_script.py input_path output_path

Uso desde un script de python:
    from cleaning_script import clean_file
    clean_file(input_path, output_path)
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import sys

from data_cleaner import DataCleaner

DEFAULT_INPUT_PATH = "input-filename.csv"
DEFAULT_OUTPUT_PATH = "output-filename.csv"

RULES = [
    # ___________________________________________
    # acá deben escribirse las reglas de limpieza
    # ___________________________________________
]


def custom_cleaning_before_rules(dc):
    """Script de limpieza custom para aplicar al objeto antes de las reglas.

    Args:
        dc (DataCleaner): Objeto data cleaner con datos cargados.
    """
    pass


def custom_cleaning_after_rules(dc):
    """Script de limpieza custom para aplicar al objeto después de las reglas.

    Args:
        dc (DataCleaner): Objeto data cleaner con datos cargados.
    """
    pass


class MyDataCleaner(DataCleaner):

    """Extensión del DataCleaner que permite agregar nuevas reglas.

    El método clean_file() utiliza esta clase extendible del DataCleaner para
    permitir el agregado de nuevos métodos de limpieza que sean necesarios, en
    un formato que haga sencilla su posterior portación al paquete original."""

    def nueva_regla(self, field, sufix=None, keep_original=False,
                    inplace=False):
        """One liner sobre lo que hace la regla.

        Descripción extendida (si correponde) sobre lo que hace la regla.

        Args:
            field (str): Campo a limpiar.
            sufix (str): Sufijo del nuevo campo creado después de limpiar.
            keep_original (bool): True si se mantiene el campo original y el
                nuevo se agrega con un sufijo. False para reemplazar el campo
                original.
            inplace (bool): True si los cambios deben impactar en el estado del
                objeto. False si sólo se quiere retornar una serie limpia sin
                impactar en el estado del objeto.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        # si no se provee un sufijo, se utiliza el default
        sufix = sufix or self.DEFAULT_SUFIX

        # debe normalizarse el nombre del campo primero
        field = self._normalize_field(field)

        # toma la serie a limpiar del DataFrame
        series = self.df[field]

        # ________________________________________________________
        # en este espacio se aplica el nuevo algoritmo de limpieza
        # y se guarda la serie limpia en una nueva variable

        clean_series = series
        # ________________________________________________________

        # guarda los cambios en el objeto, si inplace=True
        if inplace:
            self._update_series(field=field, sufix=sufix,
                                keep_original=keep_original,
                                new_series=clean_series)

        return clean_series


def clean_file(input_path, output_path):
    """Limpia los datos del input creando un nuevo archivo limpio."""

    print("Comenzando limpieza...")
    # crea una instancia de la versión extendible del DataCleaner
    dc = MyDataCleaner(input_path)

    # aplica reglas de limpieza disponibles y customizadas
    custom_cleaning_before_rules(dc)
    dc.clean(RULES)
    custom_cleaning_after_rules(dc)

    # guarda la data limpia en el csv output
    dc.save(output_path)
    print("Limpieza finalizada exitosamente!")

if __name__ == '__main__':
    # toma argumentos optativos de la línea de comandos
    if len(sys.argv) == 1:
        # el usuario no pasó argumentos, se usan los default en input y output
        clean_file(DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_PATH)
    elif len(sys.argv) == 2:
        # el usuario pasó input, se usa el default para output
        clean_file(sys.argv[1], DEFAULT_OUTPUT_PATH)
    elif len(sys.argv) == 3:
        # el usuario pasó input y output, no se usan defaults
        clean_file(sys.argv[1], sys.argv[2])
    else:
        # el usuario pasó más de 2 argumentos!
        print("{} no es una cantidad de argumentos aceptada.".format(
            len(sys.argv) - 1
        ))
