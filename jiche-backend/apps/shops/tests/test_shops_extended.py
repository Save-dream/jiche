from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.bikes.models import Bike
from apps.shops.models import Shop, UserShopVisit


class ShopExtendedAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shop_user = User.objects.create_user(
            unionid='shop_ext_union',
            nickname='扩展商家',
            shop_status=User.ShopStatus.APPROVED,
        )
        self.shop = Shop.objects.create(
            user=self.shop_user,
            name='极速摩托行',
            shop_type=Shop.ShopType.PERSONAL,
            contact_name='张老板',
            phone='13800138004',
            address='广州市天河区',
            wechat_qrcode='http://example.com/qr.jpg',
            approved_at=timezone.now(),
        )
        self.shop_user.shop_id = self.shop.id
        self.shop_user.save()
        self.user = User.objects.create_user(
            unionid='shop_ext_user',
            nickname='访问用户',
        )
        self.admin = User.objects.create_user(
            unionid='shop_ext_admin',
            nickname='管理员',
            is_staff=True,
        )
        Bike.objects.create(
            shop=self.shop,
            brand='本田',
            model='CB400',
            year=2021,
            displacement='400cc',
            mileage=8500,
            price=28000,
            engine_status='正常',
            suspension_status='正常',
            brake_status='正常',
            electrical_status='正常',
            frame_status='无事故',
            modification='无',
            defects='无',
            maintenance='良好',
            cover_image='http://example.com/cover.jpg',
            bike_status=Bike.BikeStatus.ON_SALE,
            published_at=timezone.now(),
        )
        self.user_token = AuthService().issue_tokens(self.user)['token']
        self.shop_token = AuthService().issue_tokens(self.shop_user)['token']
        self.admin_token = AuthService().issue_tokens(self.admin)['token']

    def test_shop_detail_and_visit(self):
        detail_resp = self.client.get(f'/api/shops/{self.shop.id}/')
        self.assertEqual(detail_resp.status_code, 200)
        data = detail_resp.json()['data']
        self.assertEqual(data['shop']['name'], '极速摩托行')
        self.assertEqual(len(data['bikes']), 1)

        visit_resp = self.client.post(
            '/api/visits/',
            {'shop_id': self.shop.id},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(visit_resp.status_code, 200)
        self.assertTrue(visit_resp.json()['data']['recorded'])
        self.assertEqual(UserShopVisit.objects.filter(user=self.user).count(), 1)

        visits_resp = self.client.get(
            '/api/visits/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(visits_resp.status_code, 200)
        self.assertEqual(visits_resp.json()['data']['total'], 1)

    def test_shop_profile_and_stats(self):
        profile_resp = self.client.get(
            '/api/shop/profile/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(profile_resp.status_code, 200)
        self.assertEqual(profile_resp.json()['data']['name'], '极速摩托行')

        stats_resp = self.client.get(
            '/api/shop/stats/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(stats_resp.status_code, 200)
        self.assertEqual(stats_resp.json()['data']['on_sale'], 1)

    def test_admin_shops_and_stats(self):
        list_resp = self.client.get(
            '/api/admin/shops/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(list_resp.status_code, 200)
        self.assertGreaterEqual(list_resp.json()['data']['total'], 1)

        stats_resp = self.client.get(
            '/api/admin/stats/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(stats_resp.status_code, 200)
        self.assertIn('total_shops', stats_resp.json()['data'])
