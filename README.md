data-cleaner
===

[![Coverage Status](https://coveralls.io/repos/github/datosgobar/data-cleaner/badge.svg?branch=master)](https://coveralls.io/github/datosgobar/data-cleaner?branch=master)
[![Build Status](https://travis-ci.org/datosgobar/data-cleaner.svg?branch=master)](https://travis-ci.org/datosgobar/data-cleaner)
[![PyPI](https://badge.fury.io/py/data-cleaner.svg)](http://badge.fury.io/py/data-cleaner)
[![Stories in Ready](https://badge.waffle.io/datosgobar/data-cleaner.png?label=ready&title=Ready)](https://waffle.io/datosgobar/data-cleaner)
[![Documentation Status](http://readthedocs.org/projects/data-cleaner/badge/?version=latest)](http://data-cleaner.readthedocs.org/en/latest/?badge=latest)


Paquete para limpieza de datos, según los [estándares de limpieza de la SSIPyGA](https://github.com/datosgobar/documentacion-estandares/tree/master/datos/limpieza) - Gobierno Abierto Argentina

*Nota: Este paquete aún se encuentra en etapa temprana de desarrollo y la interface podría sufrir modificaciones significativas.*

* Para referencia detallada de este paquete leer la [documentación](http://data-cleaner.readthedocs.org/en/latest/) *


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Instalación](#instalaci%C3%B3n)
  - [Dependencias](#dependencias)
  - [Tests](#tests)
- [Uso de data-cleaner](#uso-de-data-cleaner)
  - [Lista de reglas](#lista-de-reglas)
  - [Métodos de limpieza](#m%C3%A9todos-de-limpieza)
  - [Encoding del input, y otros](#encoding-del-input-y-otros)
- [Limpieza automática](#limpieza-autom%C3%A1tica)
  - [Formato del archivo limpio](#formato-del-archivo-limpio)
  - [Nombres de los campos](#nombres-de-los-campos)
  - [Saltos de línea](#saltos-de-l%C3%ADnea)
- [Template de script de limpieza](#template-de-script-de-limpieza)
- [Reglas de limpieza](#reglas-de-limpieza)
  - [Renombrar columnas (*renombrar_columnas*)](#renombrar-columnas-renombrar_columnas)
  - [Remover columnas (*remover_columnas*)](#remover-columnas-remover_columnas)
  - [Capitalizar nombres propios (*nombre_propio*)](#capitalizar-nombres-propios-nombre_propio)
  - [Dar formato a correo electrónico (*mail_format*)](#dar-formato-a-correo-electr%C3%B3nico-mail_format)
  - [Normalizar strings (*string*)](#normalizar-strings-string)
  - [Reemplazar listas de strings por valores predefinidos (*reemplazar*)](#reemplazar-listas-de-strings-por-valores-predefinidos-reemplazar)
  - [Reemplazar partes de valores (substrings) por otros (*reemplazar_string*)](#reemplazar-partes-de-valores-substrings-por-otros-reemplazar_string)
  - [Normalizar fecha completa (*fecha_completa*)](#normalizar-fecha-completa-fecha_completa)
  - [Normalizar fecha simple (*fecha_simple*)](#normalizar-fecha-simple-fecha_simple)
  - [Normalizar fecha separada en múltiples campos (*fecha_separada*)](#normalizar-fecha-separada-en-m%C3%BAltiples-campos-fecha_separada)
  - [Separar campos mediante un separador simple (*string_simple_split*)](#separar-campos-mediante-un-separador-simple-string_simple_split)
  - [Separar campos mediante una expresión regular (*string_regex_split*)](#separar-campos-mediante-una-expresi%C3%B3n-regular-string_regex_split)
  - [Separar campos mediante una parsing expression grammar (*string_peg_split*)](#separar-campos-mediante-una-parsing-expression-grammar-string_peg_split)
  - [Manipular y reemplazar contenido de campos mediante una expression regular (*string_regex_substitute*)](#manipular-y-reemplazar-contenido-de-campos-mediante-una-expression-regular-string_regex_substitute)
  - [Simplificar un objeto con datos de geometría (líneas, polígonos, etc.)](#simplificar-un-objeto-con-datos-de-geometría-líneas-polígonos-etc)
  - [Normalizar y enriquecer unidades territoriales](#normalizar-y-enriquecer-unidades-territoriales)
- [Contacto](#contacto)

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

### Dependencias

* Python 2.7

Si se va a instalar python desde cero, se recomienda instalar la distribución de **Anaconda** con Python 2.7, ya que viene con varias librerías preinstaladas.

### Tests

`nosetests` en el root del repositorio clonado (sólo para desarrollo)

## Uso de data-cleaner

### Lista de reglas

Se puede limpiar un CSV a través de una **lista de reglas**. El siguiente ejemplo toma un csv, capitaliza todos los strings en la columna "dependencia" y convierte todas las fechas de la columna "fecha_completa_audiencia" que sigan el formato *19-02-2016 09:11* al estándar ISO 8601 *2016-02-19T09:11:00-03:00*

```python
from data_cleaner import DataCleaner

input_path = "samples/example.csv"
output_path = "samples/clean_example.csv"

rules = [
    {
        "nombre_propio": [
            {"field": "dependencia"}
        ]
    },
    {
        "fecha_completa": [
            {"field": "fecha_completa_audiencia",
             "time_format": "DD-MM-YYYY HH:mm"}
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

Las reglas de limpieza del cleaner también se pueden utilizar como métodos individuales que devuelven una `pandas.DataSeries` o un `pandas.DataFrame (en el caso en que el método genere múltiples columnas nuevas).

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

En todo momento se puede acceder al `pandas.DataFrame` que contiene la tabla de datos, donde se verán reflejados los cambios luego de aplicar métodos de limpieza con el parámetro `inplace=True`.
Cuando se carga un archivo `.shp` al `DataCleaner`, éste contiene un objeto `geopandas.GeoDataFrame`, que extiende la funcionalidad de `pandas` para trabajar con geometrías.

```python
dc.df  # Accede al pandas.DataFrame o geopandas.GeoDataFrame del cleaner.
```

Para guardar el `pandas.DataFrame` en cualquier momento, probablemente luego de probar y aplicar algunas transformaciones, usar:

```python
dc.save(output_path)
```
Si se trata de un `GeoDataFrame`, puede guardarse el archivo en formatos **CSV**, **GeoJSON**, y **KML**.
Para CSVs, se puede especificar el nombre para la columna de geometría con un argumento opcional. El nombre por defecto es "geojson".

```python
dc = DataCleaner('samples/provincias/provincias.shp')
dc.save('provincias.csv', geometry_name='geojson')  # Guarda un archivo CSV con columna de geometría.
dc.save('provincias.geojson') o dc.save('provincias.json')  # Guarda un archivo GeoJSON.
dc.save('provincias.kml')  # Guarda un archivo KML.
```

El método `DataCleaner.save()` redirige al método `pandas.DataFrame.to_csv()`, y por lo tanto tienen los mismos argumentos.

### Encoding del input, y otros

Se asume que el input es un csv codificado en *utf-8*, separado por comas y que usa comillas dobles para el _enclosing_. Si alguno de estos parámetros (especialmente el _encoding_) es diferente, debe especificarse.

```python
dc = DataCleaner("ugly.csv", encoding="latin1", sep=";", quotechar="'")
```

## Limpieza automática

### Formato del archivo limpio

Luego de la limpieza, los datos se guardan siempre en un archivo *CSV*, codificado en *utf-8* separado por *","* y usando *'"'* como caracter de citas.

### Nombres de los campos

Los nombres de los campos se normalizan automáticamente. Sólo el uso de caracteres alfanuméricos ASCII y "_" está permitido. Los campos deben nombrarse con palabras en minúsculas separadas por guión bajo. Para esto el objeto:

* Reemplaza espacios y "-" por "_"
* Reemplaza todos los caracteres alfanuméricos por su versión ASCII más próxima
* Remueve todos los caracteres especiales que no sean "_"

### Saltos de línea

No se permiten saltos de línea en los valores, al momento de crear un objeto ^DataCleaner^ se reemplazan todos los saltos de línea que estén dentro del caracter de _enclosing_ (usualmente comillas dobles '"') por un espacio " ".

## Template de _script_ de limpieza

Para realizar la limpieza de un archivo CSV de datos con `data-cleaner` se sugiere utilizar el [template de script de limpieza](templates/cleaning_script.py). Este permite correr la limpieza desde la línea de comandos e implementar pasos de limpieza personalizados que exceden las funcionalidades del paquete.

## Reglas de limpieza

Son diccionarios cuyas *keys* son los nombres de las reglas de limpieza y cuyos *values* son: 
(a) lista de columnas donde aplicar la regla -en el caso en que la regla no requiera otros parámetros- o 
(b) lista de parámetros que necesita la regla para funcionar -donde el primer parámetro es siempre el campo donde aplicar la regla-.

### Renombrar columnas (*renombrar_columnas*)
Renombra columnas de la tabla de datos. 

**Especificación:**

```python
{"renombrar_columnas": [
    {"field": "columna_actual_1", "new_field": "columna_nueva_1"},
    {"field": "columna_actual_2", "new_field": "columna_nueva_2"},
    {"field": "columna_actual_3", "new_field": "columna_nueva_3"}
]}
```

**Ejemplo:**

```python
{"renombrar_columnas": [
    {"field": "aut_dependencia", "new_field": "dependencia"},
    {"field": "sujeto_obligado_audiencia", "new_field": "sujeto_obligado"}
]}
```

### Remover columnas (*remover_columnas*)
Remueve campos de la tabla de datos.

Entre otras cosas, se puede utilizar para remover los campos originales -no recomendado- que dieron origen a múltiples campos nuevos cuando se utilizó alguna regla de *split*.

**Especificación:**

```python
{"remover_columnas": [
    {"field": "columna_a_remover_1"},
    {"field": "columna_a_remover_2"}
]}
```

**Ejemplo:**

```python
{"remover_columnas": [
    {"field": "dependencia"},
    {"field": "fecha_completa_audiencia"}
]}
```

### Capitalizar nombres propios (*nombre_propio*)
Normaliza todas las palabras que encuentra poniéndolas en minúsculas y capitalizando la primera letra de cada una.

Se aplica a todos aquellos campos de datos que tengan nombres de personas. En el caso de direcciones, ciudades, países, organismos e instituciones debe aplicarse con mucha cautela, existen casos donde esta regla de limpieza hace más mal que bien (ej.: las instituciones pueden tener siglas, que no corresponde capitalizar).

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")
* **lower_words**: Lista de palabras que deben mantenerse en minúsculas, sin aplicar capitalización (Default: ["el", "los", "la", "las", "de", "del", "en", "y"])

**Especificación:**

```python
{"nombre_propio": [
    {"field": "columna_1"},
    {"field": "columna_2", "lower_words": ["lower_word1", "lower_word2"]}
]}
```

**Ejemplo:**

```python
{"nombre_propio": [
    {"field": "dependencia", "lower_words": ["en", "la"]}
    {"field": "dependencia", "lower_words": []}
    {"field": "dependencia"}
]}
```

### Dar formato a correo electrónico (*mail_format*)

Analiza todas las direcciones de correo electrónico en cada fila de una campo y les da el formato estandar definido. Es decir, las pasa todas a minúsculas y las separa con comas.

Argumentos opcionales:

* **keep_original**: True para conservar la columna original / False para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")

**Especificación:**

```python
{"mail_format": [
    {"field": "columna_1"},
    {"field": "columna_2"}
]}
```

**Ejemplo:**

```python
{"mail_format": [
    {"field": "correo_electronico"}
]}
```

### Normalizar strings (*string*)
Utiliza el algoritmo *Key Collision Fingerprint* para clusterizar strings con el mismo contenido, normalizando capitalización, acentos, caracteres especiales, etc. 

Este algoritmo busca unificar la forma de escribir strings que contienen idénticas palabras (cadenas de caracteres alfanuméricos separados por espacios) pero difieren en otros aspectos. [Para más detalle ver Key Collision Methods de OpenRefine](https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth#key-collision-methods). La implementación que se utiliza es una adaptación de [esta](https://github.com/tweirick/okstate_bioinformatics_command_line_programs/blob/master/misc_programs/FingerprintKeyer.py), publicada en Github por Tyler Weirick.

Argumentos opcionales:

* **sort_tokens**: `False` (default) para no ordenar las palabras al crear el _fingerprint_ de un string. Esto ubicará a "Sol Geriátrico" y "Geriátrico Sol" en clusters separados, sin unificar el _string_ en un sentido o en otro. Si se especifica `True`, ambos _strings_ se reescribirían de una de las dos maneras.
* **remove_duplicates**: `False` (default) para evitar remover tokens duplicados. Esto ubicará a "Sol Sol Geriátrico" en un cluster distinto a "Sol Geriátrico", sin elegir una forma de escribir el _string_ para ambos casos. Si se especifica `True`, ambos _strings_ se escribirían de una de las dos maneras.
* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")

**Especificación:**

```python
{"string": [
    {"field": "columna_1"},
    {"field": "columna_2"}
]}
```

**Ejemplo:**

```python
{"string": [
    {"field": "dependencia"},
    {"field": "lugar_audiencia"},
    {"field": "sujeto_obligado"},
    {"field": "solicitante"}
]}
```

### Reemplazar listas de strings por valores predefinidos (*reemplazar*)
Reemplaza listas de _strings_ por un valor predefinido que el usuario decide que representa a todas. Solo sirve para reemplazar valores **completos**

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")

**Especificación:**

```python
{"reemplazar": [
    {
     "field": "columna",
     "replacements": {"Nuevo1": ["Viejo"], "Nuevo2": ["ViejoA", "ViejoB"]}
    }
]}
```

**Ejemplo:**

```python
{"reemplazar": [
    {
    "field": "tipo",
    "replacements": {"Servicios": ["Serv"], "Otros": ["Otro", "Loc"]}
    }
]}

```
En este ejemplo si el campo *tipo* tuviese el valor "Serv de venta" no sería reemplazado, mientras que si tuviese el valor "Serv" sería reemplazado por "Servicios"


### Reemplazar partes de valores (substrings) por otros (*reemplazar_string*)
Reemplaza listas de substrings por otro substring. A diferencia del método *reemplazar* que reemplaza directamente valores completos, *reemplazar_string* hace reemplazos parciales. Es una versión más sencilla de *string_regex_substitute* que no permite evaluar expresiones regulares.

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")

**Especificación:**

```python
{"reemplazar_string": [
    {
     "field": "columna",
     "replacements": {"Nuevo1": ["Viejo"], "Nuevo2": ["ViejoA", "ViejoB"]}
    }
]}
```

**Ejemplo:**

```python
{"reemplazar_string": [
    {
    "field": "tipo",
    "replacements": {"Servicios": ["Serv"], "Otros": ["Otro", "Loc"]}
    }
]}
```

En este ejemplo si el campo *tipo* tuviese el valor "Serv de venta" sería reemplazado por "Servicios de Venta".

### Normalizar fecha completa (*fecha_completa*)
Estandariza un campo **con fecha y hora** a su representación en el estándar ISO 8601 (**YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]**). 

Ej.: **05-02-2016 14:53** a **2016-02-05T14:53:00-03:00**

Para el _parsing_ de fechas se utiliza la librería [*arrow*](http://crsmithdev.com/arrow/). En la regla debe especificarse el formato temporal en que la fecha está expresada en la tabla de datos original. El resultado siempre se convertirá a ISO 8601 cuando sea posible, ante cualquier error se dejará la celda vacía.

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)

**Especificación:**

```python
{"fecha_completa": [
    {"field": "columna", "time_format": "DD-MM-YYYY HH:mm"}
]}
```

**Ejemplo:**

```python
{"fecha_completa": [
    {"field": "fecha_completa_audiencia", "time_format": "DD-MM-YYYY HH:mm"}
]}
```

### Normalizar fecha simple (*fecha_simple*)
Estandariza un campo sin hora, día o mes a su representación en el estándar ISO 8601, obviando aquella parte de la representación ISO para la que no se cuenta con datos suficientes.

Ej.: **05-02-2016** a **2016-02-05**
Ej.: **02-2016** a **2016-02**

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)

**Especificación:**

```python
{"fecha_simple": [
    {"field": "columna1", "time_format": "DD-MM-YYYY"},
    {"field": "columna2", "time_format": "MM-YYYY"}
]}
```

**Ejemplo:**

```python
{"fecha_simple": [
    {"field": "fecha", "time_format": "DD-MM-YYYY"},
    {"field": "mes", "time_format": "MM-YYYY"}
]}
```

### Normalizar fecha separada en múltiples campos (*fecha_separada*)
Estandariza una fecha completa donde distintos componentes de la misma están separados en varios campos, a su representación en el estándar ISO 8601.

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)

**Especificación:**

```python
{"fecha_separada": [
    {"fields": [["campo1", "DD-MM-YYYY"], ["campo2", "HH:mm"]],
     "new_field_name": "audiencia"}
]}
```

**Ejemplo:**

```python
{"fecha_separada": [
    {"fields": [["fecha_audiencia", "DD-MM-YYYY"], ["hora_audiencia", "HH:mm"]], "new_field_name": "audiencia"}
]}
```

### Separar campos mediante un separador simple (*string_simple_split*)
Separa _strings_ de un campo en múltiples campos, mediante separadores simples.

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)

**Especificación:**

```python
{"string_simple_split": [
    {"field": "campo",
    "separators": ["separador_A", "separador_B"],
    "new_field_names": ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2"]}
]}
```

**Ejemplo:**

```python
{"string_simple_split": [
    {"field": "sujeto_obligado",
    "separators": [", Cargo:", "Cargo:"],
    "new_field_names": ["nombre", "cargo"]}
]}
```

### Separar campos mediante una expresión regular (*string_regex_split*)
(NO IMPLEMENTADO)

### Separar campos mediante una parsing expression grammar (*string_peg_split*)
Utiliza _parsing expression grammars_ para separar strings de un campo en múltiples campos.

Las PEG son una forma de utilizar expresiones regulares de más alto nivel, que facilita la creación de reglas bastante complejas. La librería que se utiliza en este paquete es [**parsley**](http://parsley.readthedocs.org/en/latest/reference.html).

Todas las PEG que se escriban para este paquete, deben contener una regla `values` cuyo _output_ sea una lista de los valores que se quiere extraer. Cuando la PEG utilizada falle, el paquete dejará un valor nulo para esa celda.

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)

**Especificación:**

```python
{"string_peg_split": [
    {"field": "campo",
    "grammar": "grammar",
    "new_field_names": ["sufijo_nuevo_campo_1", "sufijo_nuevo_campo_2"]}
]}
```

**Ejemplo:**

```python
{"string_peg_split": [
    {
    "field": "solicitante",
    "grammar": """
    allowed_char = anything:x ?(x not in '1234567890() ')
    nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
    number = <digit+>:num -> int(num)

    nom_comp = <nombre+>:nc -> nc.strip()
    cargo = '(' <nombre+>:c ')' -> c.strip()
    dni = ','? ws 'DNI' ws number:num -> num

    values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
    """,
    "new_field_names": ["nombre", "cargo", "dni"]
    }
]}
```

### Manipular y reemplazar contenido de campos mediante una expresión regular (*string_regex_substitute*)
Es análogo al método sub de la libreria de python [**re**](https://docs.python.org/2/library/re.html#re.sub).

Argumentos opcionales:

* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: False)
* **sufix**: Sufijo para agregar a la nueva columna limpia (Default: "clean")

**Especificación:**

```python
{"string_regex_substitute":[
	{"field": "campo1",
    "regex_str_match": "str_regex_match1",
    "regex_str_sub": "str_regex_replace1"},
    {"field": "campo2",
    "regex_str_match": "str_regex_match2",
    "regex_str_sub": "str_regex_replace2"}
]}
```

**Ejemplos:**

```python
Reemplaza punto y comas por comas:
{"string_regex_substitute":[
	{"field": "norma_competencias_objetivos",
    "regex_str_match": ";",
    "regex_str_sub": ","}
]}

Cambia el orden de una cadena entre paréntesis:
{"string_regex_substitute":[
	{"field": "nombre_cargo",
    "regex_str_match": "(?P<cargo>\(.+\))(?P<nombre>.+)",
    "regex_str_sub": "\g<nombre> \g<cargo>"}
]}
"(presidente)Juan José Perez." pasaría a ser "Juan José Perez. (presidente)"
```

### Simplificar un objeto con datos de geometría (líneas, polígonos, etc.)
Simplifica una geometría para que resulte en un objeto de menor tamaño
y complejidad, que a la vez retenga sus características esenciales.

**Especificación:**

```python
{"simplificar_geometria": [
    {"tolerance": nivel}
]}
```

**Ejemplos:**

```python
{"simplificar_geometria": [
    {"tolerance": 0.5}
]}
```

### Normalizar y enriquecer unidades territoriales

Normaliza y enriquece unidades territoriales utilizando la [API del Servicio de Normalización de Datos Geográficos](https://georef-ar-api.readthedocs.io/es/latest/).

Argumentos obligatorios:

* **field**: Nombre del campo a normalizar.
* **entity_level**: Nivel de la unidad territorial (Entidades válidas: "provincias", "departamentos", "municipios", "localidades").

Argumentos opcionales:

* **add_code**: `True` para agregar el código de la entidad (Default: "False")
* **add_centroid**: `True` para agregar el centroide de la entidad (Default: "False")
* **add_parents**: Lista de entidades padres a agregar (Default: "None")
* **keep_original**: `True` para conservar la columna original / `False` para removerla (Default: "False")
* **filters**: Diccionario con entidades por las cuales filtrar (Default: "None". _Keywords_ válidos: "provincia_field", "departamento_field", "municipio_field").

**Especificación**

```python
{"normalizar_unidad_territorial": [
    {
        "field": "campo",
        "entity_level": "nivel_entidad"
    }
]}
```

**Ejemplos:**

```python
{"normalizar_unidad_territorial": [
        {
            "field": "nombre",
            "entity_level": "provincia"
        }
]}
```

```python
{"normalizar_unidad_territorial": [
        {
            "field": "nombre",
            "entity_level": "localidad",
            "add_code": True,
            "add_centroid": True,
            "add_parents": ['provincia', 'departamento', 'municipio'],
            "keep_original": True,
            "filters": {
                "provincia_field": "provincia",
                "departamento_field": "departamento",
                "municipio_field": "municipio"
            }
        }
]}
```

## Contacto

Te invitamos a [creanos un issue](https://github.com/datosgobar/data-cleaner/issues/new?title=Encontre un bug en data-cleaner) en caso de que encuentres algún bug o tengas feedback de alguna parte de `data-cleaner`.

Para todo lo demás, podés mandarnos tu comentario o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).
