from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.bikes.models import Bike
from apps.favorites.models import Favorite
from apps.shops.models import Shop


class FavoriteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shop_user = User.objects.create_user(
            unionid='fav_shop_union',
            nickname='收藏商家',
            shop_status=User.ShopStatus.APPROVED,
        )
        self.shop = Shop.objects.create(
            user=self.shop_user,
            name='极速摩托行',
            shop_type=Shop.ShopType.PERSONAL,
            contact_name='张老板',
            phone='13800138003',
            wechat_qrcode='http://example.com/qr.jpg',
            approved_at=timezone.now(),
        )
        self.user = User.objects.create_user(
            unionid='fav_user_union',
            nickname='收藏用户',
        )
        self.bike = Bike.objects.create(
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
            published_at=timezone.now(),
        )
        self.user_token = AuthService().issue_tokens(self.user)['token']

    def test_add_list_remove_favorite(self):
        add_resp = self.client.post(
            '/api/favorites/',
            {'bike_id': self.bike.id},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(add_resp.status_code, 200)
        self.assertEqual(Favorite.objects.filter(user=self.user, is_deleted=False).count(), 1)

        list_resp = self.client.get(
            '/api/favorites/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(list_resp.json()['data']['total'], 1)

        del_resp = self.client.delete(
            f'/api/favorites/{self.bike.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(Favorite.objects.filter(user=self.user, is_deleted=False).exists())

    def test_duplicate_favorite_returns_409(self):
        Favorite.objects.create(user=self.user, bike=self.bike, shop=self.shop)
        dup_resp = self.client.post(
            '/api/favorites/',
            {'bike_id': self.bike.id},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(dup_resp.status_code, 409)
        self.assertEqual(dup_resp.json()['msg'], '已在收藏夹中')
        self.assertEqual(Favorite.objects.filter(user=self.user, is_deleted=False).count(), 1)

    def test_deleted_bike_shows_unavailable(self):
        Favorite.objects.create(user=self.user, bike=self.bike, shop=self.shop)
        self.bike.is_deleted = True
        self.bike.save()
        list_resp = self.client.get(
            '/api/favorites/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        item = list_resp.json()['data']['list'][0]
        self.assertTrue(item.get('unavailable'))
