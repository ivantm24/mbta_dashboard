import datetime
import http.client
import json
import time

from services import cache

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

ATTRIBUTE_TAG = 'attributes'


class MbtaService:

    def __init__(self, host, api_key=None):
        self.host = host
        self.api_key = api_key

    def _requires_read(self, path, last_modified: str):
        try:
            last_modified_tp = time.mktime(datetime.datetime.strptime(last_modified, DATE_FORMAT).timetuple())
            c_last_modified = cache.get_last_modified(path)
            if c_last_modified is None:
                return True
            c_last_modified_tp = time.mktime(datetime.datetime.strptime(c_last_modified, DATE_FORMAT).timetuple())
            if last_modified_tp <= c_last_modified_tp:
                return False
        except ValueError:
            pass
        return True

    def _request(self, conn, path):
        headers = {}
        if self.api_key is not None:
            headers['api_key'] = self.api_key
        conn.request('GET', path, headers=headers)
        res = conn.getresponse()
        last_modified = res.headers['last-modified']
        if self._requires_read(path, last_modified):
            data = res.read()
            cache.set_response(path, data)
            cache.set_last_modified(path, last_modified)
            json_obj = json.loads(data)
        else:
            json_obj = json.loads(cache.get_response(path))
        return json_obj

    def get_predictions(self, stop_id):
        path = f'/predictions?filter[stop]={stop_id}&include=route,trip,vehicle,schedule,stop&sort=departure_time'
        conn = http.client.HTTPSConnection(self.host)
        try:
            json_obj = self._request(conn, path)

            maps = {'vehicle': {}, 'trip': {}, 'route': {}, 'schedule': {}, 'stop': {}}
            for inc in json_obj['included']:
                obj_type = inc['type']
                obj_id = inc['id']
                if obj_type in maps:
                    obj_map = maps[obj_type]
                    obj_map[obj_id] = inc[ATTRIBUTE_TAG]
            for p in json_obj['data']:
                for r_name, r_content in p['relationships'].items():
                    if r_name in maps:
                        obj_map = maps[r_name]
                        r_data = r_content['data']
                        if r_data is None:
                            continue
                        obj_id = r_data['id']
                        r_data[ATTRIBUTE_TAG] = obj_map[obj_id]
        finally:
            conn.close()
        return json_obj

    def get_stops(self):
        path = '/stops'
        conn = http.client.HTTPSConnection(self.host)
        try:
            json_obj = self._request(conn, path)
        finally:
            conn.close()
        return json_obj
