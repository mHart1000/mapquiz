from django.contrib.gis.geos import MultiPolygon, Polygon
from rest_framework.test import APITestCase

from .models import City, Neighborhood


def square(x, y):
    return MultiPolygon(Polygon(((x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x, y))))


class NeighborhoodListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name='San Diego')
        Neighborhood.objects.create(city=cls.city, name='North Park', geometry=square(0, 0))
        Neighborhood.objects.create(city=cls.city, name='Ocean Beach', geometry=square(2, 2))

    def test_neighborhoods_are_anonymized(self):
        res = self.client.get('/api/cities/san-diego/neighborhoods/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 2)
        for feature in data['features']:
            self.assertNotIn('name', feature['properties'])
            self.assertIsNotNone(feature['geometry'])


class QuizRoundTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name='San Diego')
        cls.names = ['North Park', 'Ocean Beach', 'La Jolla', 'Barrio Logan', 'Uptown']
        cls.hoods = {
            name: Neighborhood.objects.create(city=cls.city, name=name, geometry=square(i, i))
            for i, name in enumerate(cls.names)
        }

    def start_round(self):
        res = self.client.get('/api/cities/san-diego/quiz/round/')
        self.assertEqual(res.status_code, 200)
        return res.json()

    def question(self, seed, index):
        return self.client.get(
            '/api/cities/san-diego/quiz/question/', {'round': seed, 'index': index}
        ).json()

    def test_round_reports_every_neighborhood(self):
        self.assertEqual(self.start_round()['total'], len(self.names))

    def test_round_asks_each_neighborhood_exactly_once(self):
        data = self.start_round()
        asked = [self.question(data['round'], i)['target_name'] for i in range(data['total'])]
        self.assertCountEqual(asked, self.names)

    def test_same_seed_reproduces_the_same_order(self):
        first = [self.question(1234, i)['target_name'] for i in range(len(self.names))]
        second = [self.question(1234, i)['target_name'] for i in range(len(self.names))]
        self.assertEqual(first, second)

    def test_round_ends_after_the_last_question(self):
        data = self.question(1234, len(self.names))
        self.assertTrue(data['done'])

    def test_question_rejects_malformed_input(self):
        res = self.client.get('/api/cities/san-diego/quiz/question/', {'round': 'x', 'index': 0})
        self.assertEqual(res.status_code, 400)

    def test_answer_scores_against_the_server_side_target(self):
        target_name = self.question(1234, 0)['target_name']
        target = self.hoods[target_name]
        other = next(h for n, h in self.hoods.items() if n != target_name)

        ok = self.client.post('/api/cities/san-diego/quiz/answer/',
                              {'round': 1234, 'index': 0, 'clicked_id': target.id}, format='json')
        self.assertEqual(ok.json(), {
            'correct': True, 'correct_id': target.id,
            'correct_name': target_name, 'clicked_name': target_name,
        })

        wrong = self.client.post('/api/cities/san-diego/quiz/answer/',
                                 {'round': 1234, 'index': 0, 'clicked_id': other.id}, format='json')
        self.assertEqual(wrong.json(), {
            'correct': False, 'correct_id': target.id,
            'correct_name': target_name, 'clicked_name': other.name,
        })

    def test_answer_reports_a_click_that_missed_every_shape(self):
        data = self.client.post('/api/cities/san-diego/quiz/answer/',
                                {'round': 1234, 'index': 0, 'clicked_id': None},
                                format='json').json()
        self.assertFalse(data['correct'])
        self.assertIsNone(data['clicked_name'])

    def test_answer_rejects_a_non_numeric_id(self):
        res = self.client.post('/api/cities/san-diego/quiz/answer/',
                               {'round': 'nope', 'index': 0, 'clicked_id': 'abc'}, format='json')
        self.assertEqual(res.status_code, 400)


class LoaderTests(APITestCase):
    """The importer must stay dataset-agnostic: no city-specific names in code."""

    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name='San Diego')

    def load(self, features, **opts):
        import json
        import tempfile
        from django.core.management import call_command

        collection = {'type': 'FeatureCollection', 'features': features}
        with tempfile.NamedTemporaryFile('w', suffix='.geojson', delete=False) as f:
            json.dump(collection, f)
            path = f.name
        call_command('load_neighborhoods', path, city='san-diego', **opts)

    @staticmethod
    def feature(name, x=0, y=0, key='CPNAME'):
        return {
            'type': 'Feature',
            'properties': {key: name, 'OBJECTID': x * 100 + y},
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x, y]]],
            },
        }

    def test_detects_the_name_property_without_being_told(self):
        self.load([self.feature('NORTH PARK', 0, 0), self.feature('OCEAN BEACH', 2, 2)])
        self.assertCountEqual(
            self.city.neighborhoods.values_list('name', flat=True),
            ['North Park', 'Ocean Beach'],
        )

    def test_merges_same_named_features_instead_of_overwriting(self):
        self.load([self.feature('NAVAJO', 0, 0), self.feature('NAVAJO', 5, 5)])
        self.assertEqual(self.city.neighborhoods.count(), 1)
        navajo = self.city.neighborhoods.get()
        self.assertEqual(len(navajo.geometry), 2)

    def test_skip_name_drops_a_feature(self):
        self.load(
            [self.feature('NORTH PARK', 0, 0), self.feature('RESERVE AREA', 2, 2)],
            skip_name=['RESERVE AREA'],
        )
        self.assertCountEqual(
            self.city.neighborhoods.values_list('name', flat=True), ['North Park']
        )

    def test_strips_a_grouping_prefix_the_source_repeats(self):
        self.load([
            self.feature('MID-CITY:CITY HEIGHTS', 0, 0),
            self.feature('MID-CITY:NORMAL HEIGHTS', 2, 2),
        ])
        self.assertCountEqual(
            self.city.neighborhoods.values_list('name', flat=True),
            ['City Heights', 'Normal Heights'],
        )

    def test_keeps_roman_numerals_uppercase(self):
        self.load([self.feature('SUBAREA II', 0, 0)])
        self.assertEqual(self.city.neighborhoods.get().name, 'Subarea II')

    def test_rename_overrides_the_display_name(self):
        self.load([self.feature('RANCHO PENASQUITOS', 0, 0)],
                  rename=['RANCHO PENASQUITOS=Rancho Peñasquitos'])
        self.assertEqual(self.city.neighborhoods.get().name, 'Rancho Peñasquitos')
