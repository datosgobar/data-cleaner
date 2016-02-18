data-cleaner
===

[![Coverage Status](https://coveralls.io/repos/gobabiertoAR/data-cleaner/badge.svg?branch=master)](https://coveralls.io/r/gobabiertoAR/data-cleaner?branch=master)
[![Build Status](https://travis-ci.org/gobabiertoAR/data-cleaner.svg?branch=master)](https://travis-ci.org/gobabiertoAR/data-cleaner)
[![PyPI](https://badge.fury.io/py/data-cleaner.svg)](http://badge.fury.io/py/data-cleaner)

Paquete para limpieza de datos, según estándares de la SSIPyGA - Gobierno Abierto Argentina

*Nota: Este paquete aún se encuentra en etapa de desarrollo y no tiene ninguna versión estable utilizable. Sólo para uso de desarrolladores de la SSIPyGA.*

## Instalación

Para desarrollo:
```
cd package_directory
pip install -e .
```

Para uso simple:
```
pip install data_cleaner
```

## Uso

### Ejemplo de uso integrador

*Nota: las reglas `string`, `string_regex_split` y `string_peg_split` todavía no fueron implementadas y por lo tanton no están disponibles para su uso.*

Cómo usar el paquete para limpiar un CSV completo utilizando un set de reglas.

```python
from data_cleaner import DataCleaner
# from tests.rules.integration import rules

input_path = "tests/input/to_clean_integration.csv"
output_path = "tests/output/temp_clean_integration.csv"

rules = [
    {
        "nombre_propio": ["dependencia"]
    },
    {
        "string": [
            "dependencia",
            "lugar_audiencia",
            "sujeto_obligado",
            "solicitante"
        ]
    },
    {
        "fecha_completa": [
            ["fecha_completa_audiencia", "DD-MM-YYYY HH:mm"]
        ]
    },
    {
        "fecha_separada": [
            [[["fecha_audiencia", "DD-MM-YYYY"], ["hora_audiencia", "HH:mm"]], 
            "audiencia"]
        ]
    },
    {
        "string_simple_split": [
            ["sujeto_obligado", [", Cargo:", "Cargo:"], ["nombre", "cargo"]]
        ]
    },
    {
        "string_regex_split": []
    },
    {
        "string_peg_split": [
            ["solicitante",
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
             ]
        ]
    }
]

dc = DataCleaner(input_path)
dc.clean_file(rules, output_path)
```

### Ejemplos de uso individuales

Las reglas de limpieza del cleaner también se pueden utilizar como métodos individuales que devuelven una pandas.DataSeries. 

En los casos más simples, el único argumento del método es el campo al que debe aplicarse.

```python
nombre_propio_series = dc.nombre_propio("dependencia")
dependencia_series = nombre_propio_series[0]

print list(dependencia_series)
["Presidencia De La Nación",
"Presidencia De La Nación",
"Presidencia De La Nación",
"Presidencia De La Nación",
"Presidencia De La Nación"]
```

En los casos en que la regla requiere parámetros (además del campo al que debe aplicarse) estos deben pasarse al método en el mismo orden en que figuran en la lista del [ejemplo integrador](#ejemplo-de-uso-integrador).

```python
string_simple_split_series = dc.string_simple_split(
    "sujeto_obligado", 
    [", Cargo:", "Cargo:"], 
    ["nombre", "cargo"]
    )
sujeto_obligado_nombre_series = string_simple_split_series[0]
sujeto_obligado_cargo_series = string_simple_split_series[1]

print list(sujeto_obligado_nombre_series)
["ABAL MEDINA, Juan Manuel",
"ABAL MEDINA, Juan Manuel",
"ABAL MEDINA, Juan Manuel",
NaN,
NaN]

print list(sujeto_obligado_cargo_series)
["Jefe de Gabinete de Ministros",
"Jefe de Gabinete de Ministros",
NaN,
NaN,
NaN]
```

Si se desea que la limpieza practicada perdure en el objeto, se debe especificar el parámetro de diccionario `inplace=True`.

```python
nombre_propio_series = dc.nombre_propio("dependencia", inplace=True)
```

En todo momento se puede acceder al pandas.DataFrame que contiene la tabla de datos, donde se verán reflejados los cambios luego de aplicar métodos de limpieza con el parámetro `inplace=True`.

```python
dc.df  # accede al pandas.DataFrame del cleaner
```

Si se desea guardar el pandas.DataFrame tal como está, probablemente luego de aplicar algunas transformaciones, se puede utilizar el método 
`DataCleaner.save()` que no es otra cosa que un wrapper del método `pandas.DataFrame.to_csv()`

```python
dc.save(output_path)
```

## Reglas disponibles

* **remover_columnas**: Remueve columnas.
    - "remover_columnas": ["remover_columna_1", "remover_columna_2"]
* **nombre_propio**: Capitaliza todas las palabras.
    - "nombre_propio": ["capitalizar_columna_1", "capitalizar_columna_2"]
* **string**: NO IMPLEMENTADO
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
             """
            allowed_char = anything:x ?(x not in '1234567890() ')
            nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
            number = <digit+>:num -> int(num)

            nom_comp = <nombre+>:nc -> nc.strip()
            cargo = '(' <nombre+>:c ')' -> c.strip()
            dni = ','? ws 'DNI' ws number:num -> num

            values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
            """,
            ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2", "sufijo_nuevo_campo_3"]
             ]
        ]

## TODO

* filtros
* clustering

