import http.client
import json


class MbtaService:
    def __init__(self, host, api_key=None):
        self.host = host
        self.api_key = api_key

    def get_stops(self):
        path = '/stops'
        conn = http.client.HTTPSConnection(self.host)
        headers = {}
        if self.api_key is not None:
            headers['api_key'] = self.api_key
        try:
            conn.request('GET', path, headers=headers)
            res = conn.getresponse()
            json_obj = json.loads(res.read())
        finally:
            conn.close()
        return json_obj
