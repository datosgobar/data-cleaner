#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json


# TODO: tomar de una variable de entorno
API_URL = 'http://localhost:5000/api/'


class GeorefWrapper:
    """Interfaz para la API REST de Georef."""

    def __init__(self):
        self.url = API_URL

    def search_state(self, search_name):
        entity = 'provincias'
        return self._get_response(entity, search_name)

    def search_departament(self, search_name):
        entity = 'departamentos'
        return self._get_response(entity, search_name)

    def search_municipality(self, search_name):
        entity = 'municipios'
        return self._get_response(entity, search_name)

    def search_locality(self, search_name):
        entity = 'localidades'
        return self._get_response(entity, search_name)

    def _get_response(self, entity, search_name):
        resource = self.url + entity + '?'
        resource += urllib.urlencode({'nombre': search_name})
        results = json.loads(urllib.urlopen(resource).read())
        return self._get_first_element(results, entity)

    @staticmethod
    def _get_first_element(results, entity):
        return results[entity][0]['nombre']
