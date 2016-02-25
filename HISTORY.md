=======
History
=======

0.1.0 (2016-2-18)
------------------

* First release on PyPI.

0.1.7 (2016-2-22)
------------------

* Se agregan nuevos métodos de limpieza.
* Se modifica la interfaz de la lista de reglas.

0.1.8 (2016-2-22)
------------------

* Se mejora el capitalizer de la regla nombre_propio()
* Se permite controlar al usuario si la o las columnas originales objeto de una limpieza se mantienen o se remueven

0.1.10 (2016-2-23)
------------------

* Corrige bug en capitalizer() cuando el input es un integer o float
* Corrige bug en métodos que parsean fechas, devuelven empty string "" en lugar de NaN

0.1.12 (2016-2-23)
------------------
* Corrige varios problemas de encoding
* Chequea que no haya campos repetidos antes de cargar un csv
