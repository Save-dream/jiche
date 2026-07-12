from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Brand, BrandModel


class CatalogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        call_command('seed_catalog')

    def test_brand_list_api(self):
        resp = self.client.get('/api/brands/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertGreaterEqual(len(data), 10)
        self.assertEqual(data[0]['name'], '本田')

    def test_brand_models_api(self):
        brand = Brand.objects.get(name='本田')
        resp = self.client.get(f'/api/brands/{brand.id}/models/')
        self.assertEqual(resp.status_code, 200)
        models = resp.json()['data']
        self.assertIn('CB400', models)
        self.assertEqual(BrandModel.objects.filter(brand=brand).count(), len(models))
