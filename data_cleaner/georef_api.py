#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

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
LOC = 'localidad'
LAT = 'centroide_lat'
LON = 'centroide_lon'


class GeorefWrapper:
    """Interfaz para la API REST de Georef."""

    def __init__(self):
        self.url = "http://apis.datos.gob.ar/georef/api/"
        self.max_bulk_len = 5000

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
        result = []
        result_partial = []
        data_len = len([i for i in data[entity] if i])
        resource = self.url + entity

        # Valida si es necesario compaginar la data a enviar
        if data_len > self.max_bulk_len:
            data = self._getrows_byslice(
                entity, data[entity], self.max_bulk_len)
        else:
            data = [data]

        for row in data:
            r = requests.post(resource, json=row)
            if 'resultados' in r.content.decode('utf8'):
                result_partial.append(json.loads(r.content)['resultados'])
            else:
                error = self._get_first_error(json.loads(r.content)['errores'])
                return {'error': error}

        for row in result_partial:
            for v in row:
                if v[entity]:
                    result.append({entity: [v[entity][0]]})
                else:
                    result.append({entity: []})

        return result

    @staticmethod
    def _getrows_byslice(entity, seq, rowlen):
        data_slice = []
        for start in range(0, len(seq), rowlen):
            data_slice.append({entity: seq[start:start + rowlen]})
        return data_slice

    @staticmethod
    def _get_first_error(result):
        idx = next(i for i, j in enumerate(result) if j)
        return result[idx]
