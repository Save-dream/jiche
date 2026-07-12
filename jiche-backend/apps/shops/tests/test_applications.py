from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.shops.models import Shop, ShopApplication
from apps.shops.services.application_service import ApplicationService, ApplicationServiceError


def make_test_image(name='test.jpg'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buffer, format='JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class ApplicationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            unionid='apply_user_union',
            nickname='申请用户',
            phone='13600000011',
        )
        self.admin = User.objects.create_user(
            unionid='apply_admin_union',
            nickname='审核管理员',
            is_staff=True,
        )
        self.service = ApplicationService()

    def _submit_payload(self, **overrides):
        payload = {
            'name': '张三机车行',
            'shop_type': '个人商户',
            'contact_name': '张三',
            'phone': '13800138000',
            'address': '广州市天河区',
            'main_models': '本田雅马哈',
            'description': '经营二手摩托',
            'wechat_qrcode': 'http://example.com/qrcode.jpg',
            'qualification_photo': '',
        }
        payload.update(overrides)
        return payload

    def test_submit_application_sets_pending_status(self):
        result = self.service.submit_application(self.user, self._submit_payload())
        self.user.refresh_from_db()
        self.assertEqual(self.user.shop_status, User.ShopStatus.PENDING)
        self.assertEqual(result['application']['shop_status'], ShopApplication.ApplicationStatus.PENDING)

    def test_cannot_submit_when_pending(self):
        self.user.shop_status = User.ShopStatus.PENDING
        self.user.save()
        with self.assertRaises(ApplicationServiceError):
            self.service.submit_application(self.user, self._submit_payload())

    def test_enterprise_requires_qualification(self):
        with self.assertRaises(ApplicationServiceError):
            self.service.submit_application(
                self.user,
                self._submit_payload(shop_type='企业商户', qualification_photo=''),
            )

    def test_audit_approve_creates_shop(self):
        self.service.submit_application(self.user, self._submit_payload())
        application = ShopApplication.objects.get(user=self.user)
        result = self.service.audit_application(
            application_id=application.id,
            auditor=self.admin,
            action='approve',
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.shop_status, User.ShopStatus.APPROVED)
        shop = Shop.objects.get(user=self.user)
        self.assertEqual(shop.name, '张三机车行')
        self.assertEqual(self.user.shop_id, shop.id)
        self.assertEqual(result['application']['shop_status'], ShopApplication.ApplicationStatus.APPROVED)

    def test_audit_reject_allows_resubmit(self):
        self.service.submit_application(self.user, self._submit_payload())
        application = ShopApplication.objects.get(user=self.user)
        self.service.audit_application(
            application_id=application.id,
            auditor=self.admin,
            action='reject',
            reject_reason='资料不清晰',
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.shop_status, User.ShopStatus.REJECTED)
        result = self.service.submit_application(
            self.user,
            self._submit_payload(description='已补充资料'),
        )
        self.assertEqual(result['user']['shop_status'], User.ShopStatus.PENDING)
        self.assertEqual(ShopApplication.objects.filter(user=self.user).count(), 2)


class ApplicationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            unionid='api_apply_user',
            nickname='API申请用户',
        )
        self.admin = User.objects.create_user(
            unionid='api_apply_admin',
            nickname='API管理员',
            is_staff=True,
        )
        self.user_token = AuthService().issue_tokens(self.user)['token']
        self.admin_token = AuthService().issue_tokens(self.admin)['token']

    def test_submit_and_my_application_api(self):
        payload = {
            'name': '李四机车',
            'shop_type': '个人商户',
            'contact_name': '李四',
            'phone': '13900139000',
            'address': '深圳南山',
            'main_models': '川崎宝马',
            'description': '专注进口车',
            'wechat_qrcode': 'http://example.com/qr.jpg',
        }
        resp = self.client.post(
            '/api/applications/',
            payload,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['user']['shop_status'], User.ShopStatus.PENDING)

        my_resp = self.client.get(
            '/api/applications/my/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(my_resp.status_code, 200)
        data = my_resp.json()['data']
        self.assertEqual(data['contact_name'], '李四')
        self.assertEqual(data['shop_status'], ShopApplication.ApplicationStatus.PENDING)

        me_resp = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(me_resp.json()['data']['shop_status'], User.ShopStatus.PENDING)

    def test_admin_audit_flow(self):
        application = ShopApplication.objects.create(
            user=self.user,
            name='王五摩托',
            shop_type=ShopApplication.ShopType.PERSONAL,
            contact_name='王五',
            phone='13700137000',
            wechat_qrcode='http://example.com/qr2.jpg',
            application_status=ShopApplication.ApplicationStatus.PENDING,
        )
        self.user.shop_status = User.ShopStatus.PENDING
        self.user.save()

        list_resp = self.client.get(
            '/api/admin/applications/?status=1',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(list_resp.status_code, 200)
        self.assertGreaterEqual(list_resp.json()['data']['total'], 1)

        approve_resp = self.client.post(
            f'/api/admin/applications/{application.id}/audit/',
            {'action': 'approve'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(approve_resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.shop_status, User.ShopStatus.APPROVED)
        self.assertIsNotNone(self.user.shop_id)

    def test_upload_image_api(self):
        image = make_test_image()
        resp = self.client.post(
            '/api/uploads/image/',
            {'file': image},
            format='multipart',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('/media/', resp.json()['data']['url'])

    def test_profile_shop_status_after_approve(self):
        application = ShopApplication.objects.create(
            user=self.user,
            name='赵六车行',
            shop_type=ShopApplication.ShopType.PERSONAL,
            contact_name='赵六',
            phone='13611112222',
            wechat_qrcode='http://example.com/qr3.jpg',
        )
        self.user.shop_status = User.ShopStatus.PENDING
        self.user.save()

        self.client.post(
            f'/api/admin/applications/{application.id}/audit/',
            {'action': 'approve'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )

        me_resp = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        data = me_resp.json()['data']
        self.assertEqual(data['shop_status'], User.ShopStatus.APPROVED)
        self.assertIsNotNone(data['shop_id'])
