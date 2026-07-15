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

    def test_shop_detail_status_filter(self):
        Bike.objects.create(
            shop=self.shop,
            brand='雅马哈',
            model='R3',
            year=2020,
            displacement='321cc',
            mileage=12000,
            price=22000,
            engine_status='正常',
            suspension_status='正常',
            brake_status='正常',
            electrical_status='正常',
            frame_status='无事故',
            modification='无',
            defects='无',
            maintenance='良好',
            cover_image='http://example.com/r3.jpg',
            bike_status=Bike.BikeStatus.SOLD,
            published_at=timezone.now(),
        )
        on_sale = self.client.get(f'/api/shops/{self.shop.id}/', {'status': 1})
        self.assertEqual(on_sale.status_code, 200)
        on_sale_list = on_sale.json()['data']['bikes']
        self.assertTrue(on_sale_list)
        self.assertTrue(all(b['bike_status'] == Bike.BikeStatus.ON_SALE for b in on_sale_list))

        sold = self.client.get(f'/api/shops/{self.shop.id}/', {'status': 2})
        self.assertEqual(sold.status_code, 200)
        sold_list = sold.json()['data']['bikes']
        self.assertTrue(sold_list)
        self.assertTrue(all(b['bike_status'] == Bike.BikeStatus.SOLD for b in sold_list))

    def test_admin_ban_unban_shop_bikes(self):
        on_sale = Bike.objects.get(shop=self.shop, brand='本田')
        manual_off = Bike.objects.create(
            shop=self.shop,
            brand='铃木',
            model='GSX',
            year=2019,
            displacement='250cc',
            mileage=9000,
            price=15000,
            engine_status='正常',
            suspension_status='正常',
            brake_status='正常',
            electrical_status='正常',
            frame_status='无事故',
            modification='无',
            defects='无',
            maintenance='良好',
            cover_image='http://example.com/gsx.jpg',
            bike_status=Bike.BikeStatus.OFF_SHELF,
            published_at=timezone.now(),
        )

        ban_resp = self.client.post(
            f'/api/admin/shops/{self.shop.id}/ban/',
            {'reason': '违规'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(ban_resp.status_code, 200)
        on_sale.refresh_from_db()
        manual_off.refresh_from_db()
        self.shop_user.refresh_from_db()
        self.assertEqual(on_sale.bike_status, Bike.BikeStatus.OFF_SHELF)
        self.assertTrue(on_sale.offline_by_shop_ban)
        self.assertEqual(manual_off.bike_status, Bike.BikeStatus.OFF_SHELF)
        self.assertFalse(manual_off.offline_by_shop_ban)
        self.assertFalse(self.shop_user.is_active)

        detail = self.client.get(f'/api/shops/{self.shop.id}/')
        self.assertEqual(detail.status_code, 404)
        self.assertIn('封禁', detail.json()['msg'])

        bike_detail = self.client.get(
            f'/api/bikes/{on_sale.id}/',
            {'shop_id': self.shop.id},
        )
        self.assertEqual(bike_detail.status_code, 404)
        self.assertIn('封禁', bike_detail.json()['msg'])

        me = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(me.status_code, 401)
        self.assertFalse(self.shop_user.is_active)

        unban_resp = self.client.post(
            f'/api/admin/shops/{self.shop.id}/unban/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(unban_resp.status_code, 200)
        on_sale.refresh_from_db()
        manual_off.refresh_from_db()
        self.shop_user.refresh_from_db()
        self.assertEqual(on_sale.bike_status, Bike.BikeStatus.ON_SALE)
        self.assertFalse(on_sale.offline_by_shop_ban)
        self.assertEqual(manual_off.bike_status, Bike.BikeStatus.OFF_SHELF)
        self.assertTrue(self.shop_user.is_active)

    def test_ban_then_delete_shows_closed_message(self):
        bike = Bike.objects.get(shop=self.shop, brand='本田')
        self.client.post(
            f'/api/admin/shops/{self.shop.id}/ban/',
            {'reason': '违规'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.client.delete(
            f'/api/admin/shops/{self.shop.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        detail = self.client.get(f'/api/shops/{self.shop.id}/')
        self.assertEqual(detail.status_code, 404)
        self.assertIn('注销', detail.json()['msg'])
        bike_detail = self.client.get(
            f'/api/bikes/{bike.id}/',
            {'shop_id': self.shop.id},
        )
        self.assertEqual(bike_detail.status_code, 404)
        self.assertIn('注销', bike_detail.json()['msg'])

    def test_admin_soft_delete_shop(self):
        del_resp = self.client.delete(
            f'/api/admin/shops/{self.shop.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(del_resp.status_code, 200)
        self.shop.refresh_from_db()
        self.assertTrue(self.shop.is_deleted)
        self.assertTrue(
            Bike.objects.filter(shop_id=self.shop.id, is_deleted=True).exists()
        )
        list_resp = self.client.get(
            '/api/admin/shops/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        ids = [item['id'] for item in list_resp.json()['data']['list']]
        self.assertNotIn(self.shop.id, ids)
