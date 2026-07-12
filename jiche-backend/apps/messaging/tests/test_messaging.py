from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.bikes.models import Bike
from apps.messaging.models import MessageItem, MessageThread
from apps.shops.models import Shop


class MessagingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shop_user = User.objects.create_user(
            unionid='msg_shop_union',
            nickname='留言商家',
            shop_status=User.ShopStatus.APPROVED,
        )
        self.shop = Shop.objects.create(
            user=self.shop_user,
            name='极速摩托行',
            shop_type=Shop.ShopType.PERSONAL,
            contact_name='张老板',
            phone='13800138002',
            wechat_qrcode='http://example.com/qr.jpg',
            approved_at=timezone.now(),
        )
        self.shop_user.shop_id = self.shop.id
        self.shop_user.save()
        self.user = User.objects.create_user(
            unionid='msg_user_union',
            nickname='咨询用户',
            phone='13600000001',
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
        self.shop_token = AuthService().issue_tokens(self.shop_user)['token']

    def test_create_thread_and_send_message(self):
        create_resp = self.client.post(
            '/api/message-threads/',
            {
                'bike_id': self.bike.id,
                'content': '请问可以试驾吗？',
                'contact_phone': '13600000001',
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(create_resp.status_code, 200)
        thread_id = create_resp.json()['data']['id']
        self.assertEqual(MessageThread.objects.count(), 1)

        send_resp = self.client.post(
            f'/api/message-threads/{thread_id}/messages/',
            {'content': '欢迎来店', 'sender_type': MessageItem.SenderType.SHOP},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(send_resp.status_code, 200)
        thread = MessageThread.objects.get(pk=thread_id)
        self.assertEqual(thread.unread_count_user, 1)
        self.assertEqual(thread.thread_status, MessageThread.ThreadStatus.REPLIED)

    def test_mark_read_and_shop_list(self):
        create_resp = self.client.post(
            '/api/message-threads/',
            {'bike_id': self.bike.id, 'content': '还在吗？'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        thread_id = create_resp.json()['data']['id']

        read_resp = self.client.post(
            f'/api/message-threads/{thread_id}/read/',
            {'role': 'shop'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(read_resp.status_code, 200)
        self.assertEqual(read_resp.json()['data']['unread_count_shop'], 0)

        list_resp = self.client.get(
            '/api/shop/message-threads/',
            HTTP_AUTHORIZATION=f'Bearer {self.shop_token}',
        )
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(list_resp.json()['data']['total'], 1)
