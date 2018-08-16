#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import requests


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

        results = []
        results_partial = []
        lenght_data = len([i for i in data[entity] if i])
        resource = self.url + entity

        if lenght_data > 5000:
            data = self._getrows_byslice(entity, data[entity], 5000)
        else:
            data = [data]

        for row in data:
            req = requests.post(resource, json=row)
            if 'resultados' in req.content:
                results_partial.append(json.loads(req.content)['resultados'])

        for row in results_partial:
            for v in row:
                if v[entity]:
                    results.append({entity: [v[entity][0]]})
                else:
                    results.append({entity: []})
        # TODO: Manejo de errores
        return results

    @staticmethod
    def _getrows_byslice(entity, seq, rowlen):
        data_slice = []
        for start in xrange(0, len(seq), rowlen):
            data_slice.append({entity: seq[start:start + rowlen]})
        return data_slice
