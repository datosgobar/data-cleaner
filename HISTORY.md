=======
History
=======

0.1.19 (2017-9-5)
------------------

* Se agrega funcionalidad para leer archivos geográficos (SHP) y guardarlos en CSV con una columna GEOJSON, principalmente para compatibilidad con CKAN. Se lee la proyección en el .prj (si este existe) y se re-proyecta por default a EPSG 4326, salvo se especifique lo contrario.
* Se agrega capacidad de leer archivos excel en XLSX.

0.1.18 (2016-4-30)
------------------

* Se agrega un parámetro opcional (`lower_words`) al método `nombre_propio`, para especificar palabras que no se capitalizan.


0.1.16 (2016-4-16)
------------------

* Se remueven los caracteres de salto de línea de todos los valores.
* Se detectan los fields con títulos que usan la convencion upper CamelCase para interpretar que cada mayúscula comienza una palabra distinta

0.1.15 (2016-3-7)
------------------

* Se arregla un bug en los métodos que operan con strings que transformaba missings nan de pandas en strings "nan".
* Se corrige capitalizer para evitar errores con cadenas de texto vacías.

0.1.14 (2016-3-7)
------------------

* Se modifica la interfaz del algoritmo de clusterización de strings, agregando parámetros para sorting de tokens y remoción de duplicados de tokens. Ahora el algoritmo es extremadamente seguro, el default está en False en ambos casos con lo cual no reordena tokens ni elimina duplicados. 
* El método clean no permite guardar un dataset en un CSV con formato que no sea el estándar.
* Las columnas nuevas se agregan en orden, justo después de las originales.
* Nueva regla de limpieza: reemplazo simple de strings (*reemplazar_string*).

0.1.13 (2016-2-25)
------------------

* Agrega método de limpieza de e-mails

0.1.12 (2016-2-23)
------------------

* Corrige varios problemas de encoding
* Chequea que no haya campos repetidos antes de cargar un csv

0.1.10 (2016-2-23)
------------------

* Corrige bug en capitalizer() cuando el input es un integer o float
* Corrige bug en métodos que parsean fechas, devuelven empty string "" en lugar de NaN

0.1.8 (2016-2-22)
------------------

* Se mejora el capitalizer de la regla nombre_propio()
* Se permite controlar al usuario si la o las columnas originales objeto de una limpieza se mantienen o se remueven

0.1.7 (2016-2-22)
------------------

* Se agregan nuevos métodos de limpieza.
* Se modifica la interfaz de la lista de reglas.

0.1.0 (2016-2-18)
------------------

* First release on PyPI.

