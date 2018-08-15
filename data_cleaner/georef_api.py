#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import os
import requests
from requests import Request


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
LAT = 'centroide_lat'
LON = 'centroide_lon'


class GeorefWrapper:
    """Interfaz para la API REST de Georef."""

    def __init__(self):
        self.url = API_URL

    def search_province(self, data):
        entity = 'provincias'
        return self._get_response(entity, data)

    def search_departament(self, data):
        entity = 'departamentos'
        return self._get_response(entity, data)

    def search_municipality(self, data):
        entity = 'municipios'
        return self._get_response(entity, data)

    def search_locality(self, data):
        entity = 'localidades'
        return self._get_response(entity, data)

    def _get_response(self, entity, data):
        resource = self.url + entity
        data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        try:
            req = requests.post(resource, data=data, headers=headers)
            if 'resultados' in req.content:
                return json.loads(req.content)['resultados']
            if 'errores' in req.content:
                msg = json.loads(req.content)['errores'][0][0]['mensaje']
                return {'error': msg}
        except Exception as e:
            return {'error': e}
