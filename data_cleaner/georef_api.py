#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
import os


API_URL = os.environ['API_URL']
ID = 'id'
NAME = 'nombre'
PROV = 'provincia'
PROV_ID = 'provincia_id'
PROV_NAM = 'provincia_nombre'
DEPT = 'departamento'
DEPT_ID = 'departamento_id'
DEPT_NAM = 'departamento_nombre'
MUN = 'municipio'
MUN_ID = 'municipio_id'
MUN_NAM = 'municipio_nombre'
LOCALITY = 'localidad'


class GeorefWrapper:
    """Interfaz para la API REST de Georef."""

    def __init__(self):
        self.url = API_URL

    def search_province(self, search_name, filters=None):
        entity = 'provincias'
        return self._get_response(entity, search_name, filters)

    def search_departament(self, search_name, filters=None):
        entity = 'departamentos'
        return self._get_response(entity, search_name, filters)

    def search_municipality(self, search_name, filters=None):
        entity = 'municipios'
        return self._get_response(entity, search_name, filters)

    def search_locality(self, search_name, filters=None):
        entity = 'localidades'
        return self._get_response(entity, search_name, filters)

    def _get_response(self, entity, search_name, filters=None,
                      first_element=True):
        params = {'nombre': search_name, 'max': 1}
        resource = self.url + entity + '?'
        if filters:
            params.update(filters)

        resource += urllib.urlencode(params)
        results = json.loads(urllib.urlopen(resource).read())
        if results[entity] and first_element:
            return self._get_first_element(results, entity)
        return results[entity]

    @staticmethod
    def _get_first_element(results, entity):
        if results[entity]:
            return results[entity][0]
