"""Offline integration tests with clearly synthetic fixtures; no downloads required."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from shapely.geometry import box, mapping

from app import app
import database
import prepare_data


def feature(geoid, name, bounds):
    return {'type': 'Feature', 'properties': {'GEOID': geoid, 'NAME': name, 'STATE': '42'},
            'geometry': mapping(box(*bounds))}


def tables(population=1000, income=60000, poverty=50, denominator=500):
    return {
        'B01003': {'estimate': {'B01003001': population}, 'error': {'B01003001': 100}},
        'B19013': {'estimate': {'B19013001': income}, 'error': {'B19013001': 5000}},
        'B17001': {'estimate': {'B17001001': denominator, 'B17001002': poverty},
                   'error': {'B17001001': 50, 'B17001002': 20}},
        'B25077': {'estimate': {'B25077001': 180000}, 'error': {'B25077001': 20000}},
    }


class TractExplorer(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.db_patch = patch.object(database, 'DB_PATH', Path(self.tmp.name) / 'test.sqlite')
        self.data_patch = patch.object(prepare_data, 'DATA_DIR', Path(self.tmp.name) / 'source')
        self.db_patch.start(); self.data_patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.db_patch.stop(); self.data_patch.stop(); self.tmp.cleanup()

    def upstream(self, url, params):
        if url.endswith('/28/query'):
            return {'type': 'FeatureCollection', 'features': [feature('4232800', 'Fixture town', (0,0,2,2))]}
        if url.endswith('/8/query'):
            # First crosses town boundary; second is inside; third only touches.
            return {'type': 'FeatureCollection', 'features': [
                feature('42043000100', 'Tract 1', (-1,0,1,2)),
                feature('42043000200', 'Tract 2', (1,0,2,2)),
                feature('42043000300', 'Touching neighbor', (2,0,3,2))]}
        if url == prepare_data.ACS:
            return {'release': {'id': 'acs2024_5yr', 'name': 'ACS 2024 5-year'}, 'data': {
                '14000US42043000100': tables(),
                '14000US42043000200': tables(population=0, income=-666666666, poverty=None, denominator=0)}}
        raise AssertionError(f'Unexpected upstream request {url}')

    def prepare(self):
        with patch.object(prepare_data, 'get_json', side_effect=self.upstream):
            response = self.client.post('/api/prepare', json={'town_id': '28:4232800'})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_preparation_join_overlap_and_rates(self):
        self.assertEqual(self.prepare()['tract_count'], 2)
        response = self.client.get('/api/tracts', params={'town_id':'28:4232800','variable':'poverty'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['features']), 2)
        self.assertEqual(data['features'][0]['properties']['value'], 10)
        self.assertIsNone(data['features'][1]['properties']['value'])
        self.assertEqual(data['features'][1]['properties']['metrics']['population']['value'], 0)
        self.assertIsNone(data['features'][1]['properties']['metrics']['income']['value'])
        # Whole geometry retained rather than falsely allocating tract estimates to town.
        self.assertEqual(min(x for x,y in data['features'][0]['geometry']['coordinates'][0]), -1)
        self.assertEqual(data['boundary']['properties']['GEOID'], '4232800')
        self.assertTrue((prepare_data.DATA_DIR / 'towns/28-4232800/prepared.json').is_file())
        self.assertEqual(self.client.get('/api/health').json()['prepared_towns'], 1)
        self.assertEqual(self.client.get('/api/towns').json()[0]['tract_count'], 2)

    def test_variables_and_reprepare_preserve_other_towns(self):
        self.prepare()
        with database.connect() as con:
            con.execute("INSERT INTO towns SELECT '28:4259000',name,year,prepared_at,boundary,source FROM towns LIMIT 1")
        self.prepare()
        self.assertEqual(len(self.client.get('/api/towns').json()), 2)
        for variable in database.VARIABLES:
            response = self.client.get('/api/tracts',params={'town_id':'28:4232800','variable':variable})
            self.assertEqual(response.status_code,200)
            self.assertEqual(len(response.json()['features']),2)
        income = self.client.get('/api/tracts',params={'town_id':'28:4232800','variable':'income'}).json()
        self.assertEqual(income['features'][0]['properties']['moe'],5000)

    def test_incomplete_download_never_replaces_prepared_town(self):
        self.prepare()
        original = self.client.get('/api/tracts',params={'town_id':'28:4232800'}).json()
        def incomplete(url, params):
            result = self.upstream(url, params)
            if url == prepare_data.ACS:
                result['data'].pop('14000US42043000200')
            return result
        with patch.object(prepare_data, 'get_json', side_effect=incomplete):
            result = self.client.post('/api/prepare',json={'town_id':'28:4232800'})
        self.assertEqual(result.status_code,502)
        self.assertEqual(self.client.get('/api/tracts',params={'town_id':'28:4232800'}).json(),original)

    def test_release_mismatch_and_invalid_parameters(self):
        def wrong_release(url, params):
            result = self.upstream(url, params)
            if url == prepare_data.ACS:
                result['release']['id'] = 'acs2023_5yr'
            return result
        with patch.object(prepare_data, 'get_json', side_effect=wrong_release):
            self.assertEqual(self.client.post('/api/prepare',json={'town_id':'28:4232800'}).status_code,502)
        self.assertEqual(self.client.get('/api/towns').json(),[])
        for town_id in ['bad', "28:42' OR 1=1", '../secrets']:
            self.assertEqual(self.client.post('/api/prepare',json={'town_id':town_id}).status_code,422)
        self.assertEqual(self.client.get('/api/tracts',params={'town_id':'28:4232800'}).status_code,404)
        self.assertEqual(self.client.get('/api/tracts',params={'town_id':'28:4232800','variable':'sql'}).status_code,422)
        self.assertEqual(self.client.get('/api/places',params={'state':"42'",'q':'Town'}).status_code,422)

    def test_search_and_static_frontend(self):
        matches = [{'town_id':'28:4232800','name':'Harrisburg city','kind':'Incorporated place','state':'42'},
                   {'town_id':'28:4259000','name':'Pittsburgh city','kind':'Incorporated place','state':'42'}]
        with patch('app.places',return_value=matches):
            self.assertEqual(len(self.client.get('/api/places',params={'state':'42','q':'harris'}).json()),1)
        for url in ['/', '/static/app.js', '/static/styles.css','/docs','/api/config','/api/health']:
            self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.client.get('/static/database.py').status_code,404)
        self.assertNotIn('City Hall',self.client.get('/').text)

    def test_missing_values_and_topcoding(self):
        for value in [None,'null',-666666666,float('nan')]:
            self.assertIsNone(prepare_data.clean_number(value))
        result = prepare_data.metrics_for(tables(income=250001))
        self.assertEqual(result['income']['value'],250000)
        self.assertTrue(result['income']['topcoded'])
        self.assertEqual(result['poverty']['value'],10)


if __name__ == '__main__':
    unittest.main()
