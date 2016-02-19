
data-cleaner
===

[![Coverage Status](https://coveralls.io/repos/gobabiertoAR/data-cleaner/badge.svg?branch=master)](https://coveralls.io/r/gobabiertoAR/data-cleaner?branch=master)
[![Build Status](https://travis-ci.org/gobabiertoAR/data-cleaner.svg?branch=master)](https://travis-ci.org/gobabiertoAR/data-cleaner)
[![PyPI](https://badge.fury.io/py/data-cleaner.svg)](http://badge.fury.io/py/data-cleaner)

Paquete para limpieza de datos, según los [estándares de limpieza de la SSIPyGA](https://github.com/gobabiertoAR/documentacion-estandares/tree/master/datos/limpieza) - Gobierno Abierto Argentina

*Nota: Este paquete aún se encuentra en etapa temprana de desarrollo y la interface podría sufrir modificaciones significativas.*

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Instalación](#instalaci%C3%B3n)
- [Uso](#uso)
  - [Ejemplo de uso integrador](#ejemplo-de-uso-integrador)
  - [Ejemplos de uso individuales](#ejemplos-de-uso-individuales)
- [Reglas disponibles](#reglas-disponibles)
- [TODO](#todo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Instalación

Para uso simple:
```
pip install data_cleaner
```

Para desarrollo:
```
cd package_directory
pip install -e .
```

## Uso

### Lista de reglas

Se puede limpiar un CSV a través de una **lista de reglas**. El siguiente ejemplo toma un csv, capitaliza todos los strings en la columna "dependencia" y convierte todas las fechas de la columna "fecha_completa_audiencia" que sigan el formato *19-02-2016 09:11* al estándar ISO 8601 *2016-02-19T09:11:00-03:00*

```python
from data_cleaner import DataCleaner

input_path = "samples/example.csv"
output_path = "samples/clean_example.csv"

rules = [
    {
        "nombre_propio": ["dependencia"]
    },
    {
        "fecha_completa": [
            ["fecha_audiencia", "DD-MM-YYYY HH:mm"]
        ]
    }
]

dc = DataCleaner(input_path)
dc.clean_file(rules, output_path)
```

### Métodos de limpieza

Las reglas de limpieza del cleaner también se pueden utilizar como métodos individuales que devuelven una pandas.DataSeries o un pandas.DataFrame (en el caso en que el método genere múltiples columnas nuevas).

```python
dependencia_clean = dc.nombre_propio("dependencia")

print dependencia_clean

0    Presidencia De La Nación
1    Presidencia De La Nación
2    Presidencia De La Nación
3    Presidencia De La Nación
4    Presidencia De La Nación
Name: dependencia, dtype: object
```

Método de limpieza con parámetros.

```python
fecha_audiencia_clean = dc.fecha_completa("fecha_audiencia",
                                          "DD-MM-YYYY HH:mm")

print fecha_audiencia_clean

0    2013-11-12T10:00:00-03:00
1    2014-12-13T10:50:00-03:00
2                          NaN
3                          NaN
4                          NaN
Name: fecha_audiencia, dtype: object
```

Si se desea que la limpieza practicada perdure en el objeto, se debe especificar el keyword argument `inplace=True`.

```python
dc.nombre_propio("dependencia", inplace=True)

print dc.df.dependencia

0    Presidencia De La Nación
1    Presidencia De La Nación
2    Presidencia De La Nación
3    Presidencia De La Nación
4    Presidencia De La Nación
Name: dependencia, dtype: object
```

En todo momento se puede acceder al pandas.DataFrame que contiene la tabla de datos, donde se verán reflejados los cambios luego de aplicar métodos de limpieza con el parámetro `inplace=True`.

```python
dc.df  # accede al pandas.DataFrame del cleaner
```

Para guardar el pandas.DataFrame en cualquier momento, probablemente luego de probar y aplicar algunas transformaciones.

```python
dc.save(output_path)
```

El método `DataCleaner.save()` redirige al método `pandas.DataFrame.to_csv()`, y por lo tanto tienen los mismos argumentos.

### Encoding

Se asume que el input es un csv encodeado en *utf-8*, separado por comas y que usa comillas dobles para el enclosing. Si alguno de estos parámetros (especialmente el enconding) es diferente, debe especificarse.

```python
dc = DataCleaner("ugly.csv", encoding="latin1", sep=";", quotechar="'")
```

## Reglas disponibles

* **remover_columnas**: Remueve columnas.
    - "remover_columnas": ["remover_columna_1", "remover_columna_2"]
* **nombre_propio**: Capitaliza todas las palabras.
    - "nombre_propio": ["capitalizar_columna_1", "capitalizar_columna_2"]
* **string**: Utiliza el algoritmo *Key Collision Fingerprint* para clusterizar strings con el mismo contenido
    - "string": ["columna_1", "columna_2"]
* **reemplazar**: Reemplaza listas de strings por un valor.
    - "reemplazar": [["columna", {"Nuevo1": ["Viejo"],
                                     "Nuevo2": ["ViejoA", "ViejoB"]}]]
* **fecha_completa**: Estandariza un campo con fecha y hora.
    - "fecha_completa": [["columna", "DD-MM-YYYY HH:mm"]]
* **fecha_simple**: Estandariza un campo sin hora, día o mes.
    - "fecha_simple": [["columna1", "DD-MM-YYYY"], ["columna2", "MM-YYYY"]]
* **fecha_separada**: Estandariza campos con fecha y hora separados.
    - "fecha_separada": [
            [[["fecha", "DD-MM-YYYY"], ["hora", "HH:mm"]], 
            "sufijo_nuevo_campo"
            ] 
* **string_simple_split**: Separa campos mediante separadores simples.
    - "string_simple_split": [
            ["campo", ["separador_A", "separador_B"], 
            ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2"]]
        ]
* **string_regex_split**: NO IMPLEMENTADO
* **string_peg_split**: Utiliza parsing expression grammars para separar un campo.
    - "string_peg_split": [
            ["campo",
            "
            allowed_char = anything:x ?(x not in '1234567890() ')
            nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
            number = <digit+>:num -> int(num)

            nom_comp = <nombre+>:nc -> nc.strip()
            cargo = '(' <nombre+>:c ')' -> c.strip()
            dni = ','? ws 'DNI' ws number:num -> num

            values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
            ",
            ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2", "sufijo_nuevo_campo_3"]
             ]
        ]

## TODO

* adivinar encoding si es posible
* evitar stopwords en las reglas que lidian con strings
* reescribir README en secciones más explicativas por regla
* normalizar los campos que definen las reglas para permitir que el usuario los escriba como aparecen originalmente
* agregar regla con filtros
* escribir test de integración
* corregir estilo de fingerprint, escribir docstrings y tests
* agregar herramienta para correr desde la línea de comandos
