from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.bikes.models import Bike
from apps.shops.models import Shop


class BikeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shop_user = User.objects.create_user(
            unionid='bike_shop_union',
            nickname='车源商家',
            phone='13800138001',
            shop_status=User.ShopStatus.APPROVED,
        )
        self.shop = Shop.objects.create(
            user=self.shop_user,
            name='极速摩托行',
            shop_type=Shop.ShopType.PERSONAL,
            contact_name='张老板',
            phone='13800138001',
            wechat_qrcode='http://example.com/qr.jpg',
            approved_at=timezone.now(),
        )
        self.shop_user.shop_id = self.shop.id
        self.shop_user.save()
        self.admin = User.objects.create_user(
            unionid='bike_admin_union',
            nickname='管理员',
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            unionid='bike_user_union',
            nickname='普通用户',
        )
        self.shop_token = AuthService().issue_tokens(self.shop_user)['token']
        self.admin_token = AuthService().issue_tokens(self.admin)['token']
        self.user_token = AuthService().issue_tokens(self.normal_user)['token']

    def _bike_payload(self, **overrides):
        payload = {
            'brand': '本田',
            'model': 'CB400',
            'year': 2021,
            'displacement': '400cc',
            'mileage': 8500,
            'transfer_count': 0,
            'price': 28000,
            'can_transfer': True,
            'negotiable': True,
            'engine_status': '正常',
            'suspension_status': '正常',
            'brake_status': '正常',
            'electrical_status': '正常',
            'frame_status': '无事故',
            'modification': '无',
            'defects': '无',
            'maintenance': '保养良好',
            'cover_image': 'http://example.com/cover.jpg',
            'images': ['http://example.com/img1.jpg'],
        }
        payload.update(overrides)
        return payload

    def test_merchant_create_and_list_bikes(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(create_resp.status_code, 200)
        bike_id = create_resp.json()['data']['id']

        list_resp = self.client.get(
            '/api/shop/bikes/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(list_resp.json()['data']['total'], 1)

        detail_resp = self.client.get(
            f'/api/bikes/{bike_id}/?shop_id={self.shop.id}',
        )
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()['data']['view_count'], 1)

    def test_off_shelf_and_admin_force_off_restore(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        bike_id = create_resp.json()['data']['id']

        off_resp = self.client.post(
            f'/api/shop/bikes/{bike_id}/off-shelf/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(off_resp.status_code, 200)
        self.assertEqual(off_resp.json()['data']['bike_status'], Bike.BikeStatus.OFF_SHELF)

        bike = Bike.objects.get(pk=bike_id)
        bike.bike_status = Bike.BikeStatus.FORCE_OFF
        bike.save()

        restore_resp = self.client.post(
            f'/api/admin/bikes/{bike_id}/restore/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(restore_resp.status_code, 200)
        self.assertEqual(restore_resp.json()['data']['bike_status'], Bike.BikeStatus.ON_SALE)

    def test_tenant_check_on_detail(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        bike_id = create_resp.json()['data']['id']
        wrong_shop_resp = self.client.get(f'/api/bikes/{bike_id}/?shop_id=9999')
        self.assertEqual(wrong_shop_resp.status_code, 403)

    def test_off_shelf_hidden_from_c_end_detail(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        bike_id = create_resp.json()['data']['id']
        self.client.post(
            f'/api/shop/bikes/{bike_id}/off-shelf/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        detail_resp = self.client.get(f'/api/bikes/{bike_id}/?shop_id={self.shop.id}')
        self.assertEqual(detail_resp.status_code, 404)

    def test_admin_delete_bike_hidden_from_c_end(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        bike_id = create_resp.json()['data']['id']

        delete_resp = self.client.delete(
            f'/api/admin/bikes/{bike_id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(delete_resp.status_code, 200)
        self.assertTrue(Bike.objects.get(pk=bike_id).is_deleted)

        detail_resp = self.client.get(f'/api/bikes/{bike_id}/?shop_id={self.shop.id}')
        self.assertEqual(detail_resp.status_code, 404)

        shop_resp = self.client.get(f'/api/shops/{self.shop.id}/')
        self.assertEqual(shop_resp.status_code, 200)
        bike_ids = [b['id'] for b in shop_resp.json()['data']['bikes']]
        self.assertNotIn(bike_id, bike_ids)

    def test_mark_sold_and_share_link(self):
        create_resp = self.client.post(
            '/api/shop/bikes/',
            self._bike_payload(),
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        bike_id = create_resp.json()['data']['id']

        share_resp = self.client.post(
            f'/api/shop/bikes/{bike_id}/share-link/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(share_resp.status_code, 200)
        share = share_resp.json()['data']
        self.assertIn('/s/', share['short_url'])
        self.assertTrue(share['sign'])

        resolve_resp = self.client.get(f"/api/s/{share['short_code']}/")
        self.assertEqual(resolve_resp.status_code, 200)
        self.assertEqual(resolve_resp.json()['data']['bike_id'], bike_id)

        signed_detail = self.client.get(
            f"/api/bikes/{bike_id}/?shop_id={self.shop.id}"
            f"&timestamp={share['timestamp']}&sign={share['sign']}"
        )
        self.assertEqual(signed_detail.status_code, 200)

        bad_sign = self.client.get(
            f'/api/bikes/{bike_id}/?shop_id={self.shop.id}&timestamp={share["timestamp"]}&sign=bad'
        )
        self.assertEqual(bad_sign.status_code, 403)

        sold_resp = self.client.post(
            f'/api/shop/bikes/{bike_id}/mark-sold/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(sold_resp.status_code, 200)
        self.assertEqual(sold_resp.json()['data']['bike_status'], Bike.BikeStatus.SOLD)

        # 已售仍可在 C 端查看
        detail_resp = self.client.get(f'/api/bikes/{bike_id}/?shop_id={self.shop.id}')
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()['data']['bike_status'], Bike.BikeStatus.SOLD)
