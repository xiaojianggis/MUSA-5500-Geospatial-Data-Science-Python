"""Integration checks against a prepared demo database: python -m unittest -v."""
import unittest
from fastapi.testclient import TestClient
from app import app
from database import connect


class CensusAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_district_counts_match_database(self):
        for category in ['all', 'w', 'b', 'a', 'h', 'o']:
            with self.subTest(category=category), connect() as con:
                expected = con.execute("SELECT count(*) FROM census_points WHERE ?='all' OR category=?",
                                       [category, category]).fetchone()[0]
                response = self.client.get('/api/districts', params={'category': category})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(sum(f['properties']['sample_dots'] for f in data['features']), expected)
                self.assertEqual(len(data['features']), 18)
                self.assertTrue(all(f['geometry']['type'] in ['Polygon','MultiPolygon'] for f in data['features']))

    def test_radius_and_category_queries(self):
        base = {'lon': -75.1636, 'lat': 39.9526}
        small = self.client.get('/api/nearby', params={**base,'radius_m':1000}).json()
        large = self.client.get('/api/nearby', params={**base,'radius_m':5000}).json()
        self.assertGreater(small['sample_dots'], 0)
        self.assertGreaterEqual(large['sample_dots'], small['sample_dots'])
        self.assertEqual(large['sample_dots'], sum(r['sample_dots'] for r in large['categories']))
        filtered = self.client.get('/api/nearby',params={**base,'radius_m':5000,'category':'b'}).json()
        expected = next(r['sample_dots'] for r in large['categories'] if r['category']=='b')
        self.assertEqual(filtered['sample_dots'], expected)

    def test_invalid_requests(self):
        for params in [{'lon':0,'lat':0,'radius_m':0},
                       {'lon':-75,'lat':40,'category':"b' OR 1=1 --"},
                       {'lon':181,'lat':40}, {'lon':-75,'lat':40,'radius_m':20001}]:
            self.assertEqual(self.client.get('/api/nearby',params=params).status_code,422)
        self.assertEqual(self.client.get('/api/nearby',params={'lon':0,'lat':0}).status_code,400)

    def test_frontend_and_health(self):
        for url in ['/', '/static/app.js', '/static/styles.css', '/docs', '/api/health']:
            self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.client.get('/static/database.py').status_code,404)


if __name__ == '__main__':
    unittest.main()
