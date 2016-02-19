
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

También se pueden limpiar los datos sin guardar el csv, para analizarlos en memoria.

```python
dc.clean(rules)
dc.df  # accede al DataFrame donde están los datos
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

### Encoding del input, y otros

Se asume que el input es un csv encodeado en *utf-8*, separado por comas y que usa comillas dobles para el enclosing. Si alguno de estos parámetros (especialmente el enconding) es diferente, debe especificarse.

```python
dc = DataCleaner("ugly.csv", encoding="latin1", sep=";", quotechar="'")
```

## Limpieza automática

### Formato del archivo limpio

Luego de la limpieza los datos se guardan siempre en un archivo *CSV*, encodeado en *utf-8* separado por *","* y usando *'"'* como caracter de citas.

### Nombres de los campos

Los nombres de los campos se normalizan automáticamente. Sólo el uso de caracteres alfanuméricos ASCII y "_" está permitido. Los campos deben nombrarse con palabras en minúsculas separadas por guión bajo. Para esto el objeto:

* Reemplaza espacios y "-" por "_"
* Reemplaza todos los caracteres alfanuméricos por su versión ASCII más próxima
* Remueve todos los caracteres especiales que no sean "_"
    
## Reglas de limpieza

Son diccionarios cuyas *keys* son los nombres de las reglas de limpieza y cuyos *values* son (a) lista de columnas donde aplicar la regla -en el caso en que la regla no requiera otros parámetros- o (b) lista de parámetros que necesita la regla para funcionar -donde el primer parámetro es siempre el campo donde aplicar la regla-.

### Remover columnas (*renombrar_columnas*)
Renombra columnas de la tabla de datos. 

**Especificación:**
{"renombrar_columnas": [
    ["columna_actual_1", "columna_nueva_1"],
    ["columna_actual_2", "columna_nueva_2"],
    ["columna_actual_3", "columna_nueva_3"]
]}

**Ejemplo:**
{"renombrar_columnas": [
    ["aut_dependencia", "dependencia"],
    ["sujeto_obligado_audiencia", "sujeto_obligado"]
]}

### Renombrar columnas (*renombrar_columnas*)
Re campos de la tabla de datos. 

Entre otras cosas, se puede utilizar para remover los campos originales -no recomendado- que dieron origen a múltiples campos nuevos cuando se utilizó alguna regla de *split*.

**Especificación:**
{"remover_columnas": ["columna_a_remover_1", "columna_a_remover_2"]}

**Ejemplo:**
{"remover_columnas": ["dependencia", "fecha_completa_audiencia"]}

### Capitalizar nombres propios (*nombre_propio*)
Normaliza todas las palabras que encuentra poniéndolas en minúsculas y capitalizando la primera letra de cada una.

Se aplica a todos aquellos campos de datos que tengan nombres de personas. En el caso de direcciones, ciudades, países, organismos e instituciones debe aplicarse con mucha cautela, existen casos donde esta regla de limpieza hace más mal que bien (ej.: las instituciones pueden tener siglas, que no corresponde capitalizar).

**Especificación:**
{"nombre_propio": ["columna_1", "columna_2"]}

**Ejemplo:**
{"nombre_propio": ["dependencia"]}

### Normalizar strings (*string*)
Utiliza el algoritmo *Key Collision Fingerprint* para clusterizar strings con el mismo contenido, normalizando capitalización, acentos, caracteres especiales, orden de las palabras, etc. 

Este algoritmo busca unificar la forma de escribir strings que contienen idénticas palabras (cadenas de caracteres alfanuméricos separados por espacios) pero difieren en otros aspectos. [Para más detalle ver Key Collision Methods de OpenRefine](https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth#key-collision-methods). La implementación que se utiliza es una adaptación de [esta](https://github.com/tweirick/okstate_bioinformatics_command_line_programs/blob/master/misc_programs/FingerprintKeyer.py), publicada en Github por Tyler Weirick.

**Especificación:**
{"string": ["columna_1", "columna_2"]}

**Ejemplo:**
{"string": ["dependencia", "lugar_audiencia", "sujeto_obligado", 
            "solicitante"]}

### Reemplazar listas de strings por valores predefinidos (*reemplazar*)
Reemplaza listas de strings por un valor predefinido que el usuario decide que representa a todas.

**Especificación:**
{"reemplazar": [
    ["columna", {"Nuevo1": ["Viejo"], "Nuevo2": ["ViejoA", "ViejoB"]}]
]}

**Ejemplo:**
{"reemplazar": [
    ["tipo", {"Servicios": ["Serv"], "Otros": ["Otro", "Loc"]}]
]}

### Normalizar fecha completa (*fecha_completa*)
Estandariza un campo **con fecha y hora** a su representación en el estándar ISO 8601 (**YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]**). 

Ej.: **05-02-2016 14:53** a **2016-02-05T14:53:00-03:00**

Para el parsing de fechas se utiliza la librería [*arrow*](http://crsmithdev.com/arrow/). En la regla debe especificarse el formato temporal en que la fecha está expresada en la tabla de datos original. El resultado siempre se convertirá a ISO 8601 cuando sea posible, ante cualquier error se dejará la celda vacía.

**Especificación:**
{"fecha_completa": [
    ["columna", "DD-MM-YYYY HH:mm"]
]}

**Ejemplo:**
{"fecha_completa": [
    ["fecha_completa_audiencia", "DD-MM-YYYY HH:mm"]
]}

### Normalizar fecha simple (*fecha_simple*)
Estandariza un campo sin hora, día o mes a su representación en el estándar ISO 8601, obviando aquella parte de la representación ISO para la que no se cuenta con datos suficientes.

Ej.: **05-02-2016** a **2016-02-05**
Ej.: **02-2016** a **2016-02**

**Especificación:**
{"fecha_simple": [
    ["columna1", "DD-MM-YYYY"], 
    ["columna2", "MM-YYYY"]
]}

**Ejemplo:**
{"fecha_simple": [
    ["fecha", "DD-MM-YYYY"], 
    ["mes", "MM-YYYY"]
]}

### Normalizar fecha separada en múltiples campos (*fecha_separada*)
Estandariza una fecha completa donde distintos componentes de la misma están separados en varios campos, a su representación en el estándar ISO 8601.

**Especificación:**
{"fecha_separada": [
    [[["campo1", "DD-MM-YYYY"], ["campo2", "HH:mm"]], "audiencia"]
]}

**Ejemplo:**
{"fecha_separada": [
    [[["fecha_audiencia", "DD-MM-YYYY"], ["hora_audiencia", "HH:mm"]], "audiencia"]
]}

### Separar campos mediante un separador simple (*string_simple_split*)
Separa strings de un campo en múltiples campos, mediante separadores simples.

**Especificación:**
{"string_simple_split": [
    ["campo", ["separador_A", "separador_B"], ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2"]]
]}

**Ejemplo:**
{"string_simple_split": [
    ["sujeto_obligado", [", Cargo:", "Cargo:"], ["nombre", "cargo"]]
]}

### Separar campos mediante una expresión regular (*string_regex_split*)
(NO IMPLEMENTADO)

### Separar campos mediante una parsing expression grammar (*string_peg_split*)
Utiliza parsing expression grammars para separar un strings de un campo en múltiples campos.

Las PEG son una forma de utilizar expresiones regulares de más alto nivel, que facilita la creación de reglas bastante complejas. La librería que se utiliza en este paquete es [**parsley**](http://parsley.readthedocs.org/en/latest/reference.html).

**Especificación:**
{"string_peg_split": [
    ["campo", "grammar", ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2"]]
]}

**Ejemplo:**
{"string_peg_split": [
    [
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
    ]
]}

## TODO

* reescribir README en secciones más explicativas por regla
* evitar stopwords en las reglas que lidian con strings
* adivinar encoding si es posible
* corregir estilo de fingerprint, escribir docstrings y tests
* agregar regla para filtros
* escribir test de integración
* agregar herramienta para correr desde la línea de comandos
