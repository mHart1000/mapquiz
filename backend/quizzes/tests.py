from django.contrib.gis.geos import MultiPolygon, Polygon
from rest_framework.test import APITestCase

from .models import City, Neighborhood


def square(x, y):
    return MultiPolygon(Polygon(((x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x, y))))


class QuizEndpointTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name='San Diego')
        cls.np = Neighborhood.objects.create(city=cls.city, name='North Park', geometry=square(0, 0))
        cls.ob = Neighborhood.objects.create(city=cls.city, name='Ocean Beach', geometry=square(2, 2))

    def test_neighborhoods_are_anonymized(self):
        res = self.client.get('/api/cities/san-diego/neighborhoods/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 2)
        # name must not leak to the client
        self.assertNotIn('name', data['features'][0]['properties'])

    def test_question_returns_a_known_name(self):
        res = self.client.get('/api/cities/san-diego/quiz/question/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(res.json()['target_name'], {'North Park', 'Ocean Beach'})

    def test_answer_validates_correct_and_incorrect(self):
        ok = self.client.post('/api/cities/san-diego/quiz/answer/',
                              {'target_name': 'North Park', 'clicked_id': self.np.id}, format='json')
        self.assertEqual(ok.json(), {'correct': True, 'correct_id': self.np.id})

        wrong = self.client.post('/api/cities/san-diego/quiz/answer/',
                                {'target_name': 'North Park', 'clicked_id': self.ob.id}, format='json')
        self.assertEqual(wrong.json(), {'correct': False, 'correct_id': self.np.id})
