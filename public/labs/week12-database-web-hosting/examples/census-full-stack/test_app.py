"""Offline county/tract integration tests with synthetic fixtures and temporary storage."""
import csv
import io
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
    return {'type': 'Feature', 'properties': {'GEOID': geoid, 'NAME': name, 'STATE': geoid[:2]},
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
        if url.endswith('/82/query'):
            return {'type': 'FeatureCollection', 'features': [feature('42043', 'Dauphin County', (0,0,2,2))]}
        if url.endswith('/8/query'):
            self.assertIn("STATE='42'",params['where'])
            self.assertIn("COUNTY='043'",params['where'])
            # Both belong to this county by GEOID, regardless of town overlap.
            return {'type': 'FeatureCollection', 'features': [
                feature('42043000100', 'Tract 1', (-1,0,1,2)),
                feature('42043000200', 'Tract 2', (20,20,21,21))]}
        if url == prepare_data.ACS:
            return {'release': {'id': 'acs2024_5yr', 'name': 'ACS 2024 5-year'}, 'data': {
                '14000US42043000100': tables(),
                '14000US42043000200': tables(population=0, income=-666666666, poverty=None, denominator=0)}}
        raise AssertionError(f'Unexpected upstream request {url}')

    def prepare(self):
        with patch.object(prepare_data, 'get_json', side_effect=self.upstream):
            response = self.client.post('/api/prepare', json={'county_id': '42043'})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    def test_full_county_tract_selection_and_rates(self):
        self.assertEqual(self.prepare()['tract_count'],2)
        response = self.client.get('/api/tracts',params={'county_id':'42043','variable':'poverty'})
        self.assertEqual(response.status_code,200)
        data = response.json()
        self.assertEqual(data['county_name'],'Dauphin County')
        self.assertEqual(data['geography_level'],'census_tract')
        self.assertNotIn('boundary',data)
        self.assertEqual(len(data['features']),2)
        self.assertTrue(all(f['properties']['geoid'].startswith('42043') for f in data['features']))
        self.assertEqual(data['features'][0]['properties']['value'],10)
        self.assertIsNone(data['features'][1]['properties']['value'])
        self.assertEqual(data['features'][1]['properties']['metrics']['population']['value'],0)
        self.assertIsNone(data['features'][1]['properties']['metrics']['income']['value'])
        self.assertTrue((prepare_data.DATA_DIR/'counties/42043/prepared.json').is_file())
        self.assertEqual(self.client.get('/api/health').json()['prepared_counties'],1)
        self.assertEqual(self.client.get('/api/prepared-counties').json()[0]['tract_count'],2)

    def test_reprepare_preserves_other_counties_and_excludes_legacy_towns(self):
        self.prepare()
        with database.connect() as con:
            con.execute("INSERT INTO counties SELECT '34021','Mercer County',year,prepared_at,source FROM counties LIMIT 1")
            con.execute('CREATE TABLE towns (town_id TEXT)')
            con.execute("INSERT INTO towns VALUES ('28:4232800')")
        self.prepare()
        self.assertEqual(len(self.client.get('/api/prepared-counties').json()),2)
        with database.connect() as con:
            self.assertEqual(con.execute('SELECT count(*) FROM towns').fetchone()[0],1)
        for variable in database.VARIABLES:
            result=self.client.get('/api/tracts',params={'county_id':'42043','variable':variable})
            self.assertEqual(result.status_code,200)
            self.assertEqual(len(result.json()['features']),2)
        income=self.client.get('/api/tracts',params={'county_id':'42043','variable':'income'}).json()
        self.assertEqual(income['features'][0]['properties']['moe'],5000)

    def test_incomplete_download_never_replaces_prepared_county(self):
        self.prepare()
        original=self.client.get('/api/tracts',params={'county_id':'42043'}).json()
        def incomplete(url,params):
            result=self.upstream(url,params)
            if url==prepare_data.ACS: result['data'].pop('14000US42043000200')
            return result
        with patch.object(prepare_data,'get_json',side_effect=incomplete):
            response=self.client.post('/api/prepare',json={'county_id':'42043'})
        self.assertEqual(response.status_code,502)
        self.assertEqual(self.client.get('/api/tracts',params={'county_id':'42043'}).json(),original)

    def test_wrong_county_tract_is_rejected(self):
        def wrong_county(url,params):
            result=self.upstream(url,params)
            if url.endswith('/8/query'):
                result['features'].append(feature('42045000100','Neighboring county tract',(1,1,2,2)))
            return result
        with patch.object(prepare_data,'get_json',side_effect=wrong_county):
            response=self.client.post('/api/prepare',json={'county_id':'42043'})
        self.assertEqual(response.status_code,502)
        self.assertEqual(self.client.get('/api/prepared-counties').json(),[])

    def test_release_mismatch_and_invalid_parameters(self):
        def wrong_release(url,params):
            result=self.upstream(url,params)
            if url==prepare_data.ACS: result['release']['id']='acs2023_5yr'
            return result
        with patch.object(prepare_data,'get_json',side_effect=wrong_release):
            self.assertEqual(self.client.post('/api/prepare',json={'county_id':'42043'}).status_code,502)
        for county_id in ['bad',"42' OR 1=1",'../secrets','28:4232800']:
            self.assertEqual(self.client.post('/api/prepare',json={'county_id':county_id}).status_code,422)
        self.assertEqual(self.client.post('/api/prepare',json={'town_id':'28:4232800'}).status_code,422)
        self.assertEqual(self.client.get('/api/tracts',params={'county_id':'42043'}).status_code,404)
        self.assertEqual(self.client.get('/api/tracts',params={'county_id':'42043','variable':'sql'}).status_code,422)
        self.assertEqual(self.client.get('/api/counties',params={'state':"42'"}).status_code,422)

    def test_state_county_lists_and_static_frontend(self):
        for state in ['42','34']:
            matches=[{'county_id':f'{state}{i:03d}','name':f'County {i}','state_fips':state,'county_fips':f'{i:03d}'} for i in range(120)]
            with patch('app.counties',return_value=matches) as fetch_counties:
                response=self.client.get('/api/counties',params={'state':state})
                self.assertEqual(response.status_code,200)
                self.assertEqual(len(response.json()),120)
                fetch_counties.assert_called_once_with(state)
        for url in ['/','/static/app.js','/static/styles.css','/docs','/api/config','/api/health']:
            self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.client.get('/static/database.py').status_code,404)
        html=self.client.get('/').text
        self.assertIn('County</label>',html)
        self.assertNotIn('Town / municipality',html)

    def test_county_tract_exports_are_flat_and_unique(self):
        self.prepare()
        data=self.client.get('/api/dataset').json()
        self.assertEqual(data['geography_level'],'census_tract')
        self.assertNotIn('boundary',data)
        self.assertEqual(len(data['features']),2)
        for f in data['features']:
            p=f['properties']
            self.assertEqual(len(p['geoid']),11)
            self.assertEqual(p['county_geoid'],p['geoid'][:5])
            self.assertEqual(p['county_name'],'Dauphin County')
            self.assertIn('population',p)
            self.assertNotIn('metrics',p)
        response=self.client.get('/api/dataset',params={'county_id':'42043','format':'csv'})
        self.assertEqual(response.status_code,200)
        rows=list(csv.DictReader(io.StringIO(response.text)))
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['geoid'],'42043000100')
        self.assertEqual(float(rows[0]['poverty']),10)
        self.assertEqual(rows[1]['income'],'')
        exported=prepare_data.DATA_DIR.parent/'census-tracts'
        self.assertEqual(len(json.loads((exported/'acs2024_tracts.geojson').read_text())['features']),2)
        self.assertTrue((exported/'counties/42043_tracts.csv').is_file())
        self.assertFalse((exported/'areas').exists())

    def test_missing_values_and_topcoding(self):
        for value in [None,'null',-666666666,float('nan')]:
            self.assertIsNone(prepare_data.clean_number(value))
        result=prepare_data.metrics_for(tables(income=250001))
        self.assertEqual(result['income']['value'],250000)
        self.assertTrue(result['income']['topcoded'])
        self.assertEqual(result['poverty']['value'],10)


if __name__=='__main__':
    unittest.main()
