from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService


class WeChatUserMergeTests(TestCase):
    def test_mini_and_web_share_same_unionid(self):
        service = AuthService()
        mp_user = service.get_or_create_wechat_user(
            mp_openid='mp_test_1',
            unionid='union_shared',
            platform=User.LoginPlatform.MINI_PROGRAM,
        )
        web_user = service.get_or_create_wechat_user(
            web_openid='web_test_1',
            unionid='union_shared',
            platform=User.LoginPlatform.WEB,
        )
        self.assertEqual(mp_user.id, web_user.id)
        mp_user.refresh_from_db()
        self.assertEqual(mp_user.mp_openid, 'mp_test_1')
        self.assertEqual(mp_user.web_openid, 'web_test_1')


class MiniProgramLoginTests(TestCase):
    @override_settings(WECHAT_MOCK=True)
    def test_wx_mini_login_creates_user_and_token(self):
        service = AuthService()
        result = service.mini_program_login('test-code-abc')
        self.assertIn('token', result)
        self.assertIn('user', result)
        user = User.objects.get(id=result['user']['id'])
        self.assertIsNotNone(user.mp_openid)
        self.assertEqual(user.last_login_platform, User.LoginPlatform.MINI_PROGRAM)


class LoginTicketTests(TestCase):
    @override_settings(WECHAT_MOCK=True, DEBUG=True)
    def test_simulate_without_user_id_creates_dev_user(self):
        service = AuthService()
        ticket_data = service.create_login_ticket()
        user = service.simulate_login_ticket(ticket_data['ticket_id'])
        self.assertEqual(user.unionid, 'dev_simulate_unionid')
        poll = service.poll_login_ticket(ticket_data['ticket_id'])
        self.assertEqual(poll['status'], 'confirmed')

    @override_settings(WECHAT_MOCK=True, DEBUG=True)
    def test_scan_login_flow(self):
        service = AuthService()
        user = User.objects.create_user(
            unionid='union_ticket',
            mp_openid='mp_ticket',
            nickname='测试用户',
        )
        ticket_data = service.create_login_ticket()
        ticket_id = ticket_data['ticket_id']

        pending = service.poll_login_ticket(ticket_id)
        self.assertEqual(pending['status'], 'pending')

        service.simulate_login_ticket(ticket_id, user.id)
        confirmed = service.poll_login_ticket(ticket_id)
        self.assertEqual(confirmed['status'], 'confirmed')
        self.assertEqual(confirmed['user']['id'], user.id)
        self.assertIn('token', confirmed)

    @override_settings(WECHAT_MOCK=True)
    def test_confirm_ticket_with_mini_code(self):
        service = AuthService()
        ticket_data = service.create_login_ticket()
        ticket_id = ticket_data['ticket_id']
        service.confirm_login_ticket(ticket_id, code='mini-code-1')
        result = service.poll_login_ticket(ticket_id)
        self.assertEqual(result['status'], 'confirmed')
        self.assertEqual(User.objects.count(), 1)


class AdminStaffTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            unionid='union_admin',
            nickname='管理员',
            is_staff=True,
            is_super_staff=True,
        )
        self.normal = User.objects.create_user(
            unionid='union_normal',
            nickname='普通用户',
        )
        self.service = AuthService()

    def test_grant_and_revoke_staff(self):
        target = self.service.grant_staff(self.admin, self.normal)
        self.assertTrue(target.is_staff)
        target = self.service.revoke_staff(self.admin, target)
        self.assertFalse(target.is_staff)

    def test_cannot_revoke_super_staff(self):
        with self.assertRaises(ValueError):
            self.service.revoke_staff(self.admin, self.admin)

    def test_ban_then_delete_user(self):
        with self.assertRaises(ValueError):
            self.service.delete_user(self.admin, self.normal, '直接删')
        banned = self.service.ban_user(self.admin, self.normal, '违规')
        self.assertFalse(banned.is_active)
        self.assertEqual(banned.ban_reason, '违规')
        deleted = self.service.delete_user(self.admin, banned, '清理账号')
        self.assertTrue(deleted.is_deleted)
        self.assertEqual(deleted.delete_reason, '清理账号')
        active = self.service.list_admin_users('active')
        self.assertFalse(any(u['id'] == self.normal.id for u in active['list']))
        deleted_list = self.service.list_admin_users('deleted')
        self.assertTrue(any(u['id'] == self.normal.id for u in deleted_list['list']))


class AuthAPITests(TestCase):
    @override_settings(WECHAT_MOCK=True, DEBUG=True)
    def test_full_web_login_api_flow(self):
        admin = User.objects.create_user(
            unionid='union_api_admin',
            nickname='API管理员',
            is_staff=True,
            is_super_staff=True,
        )
        create_resp = self.client.post('/api/auth/login-ticket/', {}, content_type='application/json')
        self.assertEqual(create_resp.status_code, 200)
        self.assertEqual(create_resp.json()['code'], 200)
        ticket_id = create_resp.json()['data']['ticket_id']

        poll_pending = self.client.get(f'/api/auth/login-ticket/{ticket_id}/')
        self.assertEqual(poll_pending.json()['data']['status'], 'pending')

        simulate_resp = self.client.post(
            f'/api/auth/login-ticket/{ticket_id}/simulate/',
            {'user_id': admin.id},
            content_type='application/json',
        )
        self.assertEqual(simulate_resp.status_code, 200)

        poll_confirmed = self.client.get(f'/api/auth/login-ticket/{ticket_id}/')
        data = poll_confirmed.json()['data']
        self.assertEqual(data['status'], 'confirmed')
        token = data['token']

        me_resp = self.client.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()['data']['id'], admin.id)
        self.assertTrue(me_resp.json()['data']['is_staff'])

    @override_settings(WECHAT_MOCK=True, DEBUG=True)
    def test_admin_users_management_api(self):
        admin = User.objects.create_user(
            unionid='union_manage_admin',
            nickname='管理端',
            is_staff=True,
        )
        normal = User.objects.create_user(unionid='union_manage_user', nickname='待授权')
        _, token_data = self._login_as(admin)

        list_resp = self.client.get('/api/admin/users/', HTTP_AUTHORIZATION=f'Bearer {token_data}')
        self.assertEqual(list_resp.status_code, 200)
        self.assertGreaterEqual(list_resp.json()['data']['total'], 2)

        grant_resp = self.client.post(
            f'/api/admin/users/{normal.id}/grant-staff/',
            {},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token_data}',
        )
        self.assertEqual(grant_resp.status_code, 200)
        self.assertTrue(grant_resp.json()['data']['is_staff'])

        revoke_resp = self.client.post(
            f'/api/admin/users/{normal.id}/revoke-staff/',
            {},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token_data}',
        )
        self.assertEqual(revoke_resp.status_code, 200)
        self.assertFalse(revoke_resp.json()['data']['is_staff'])

    @override_settings(WECHAT_MOCK=True)
    def test_wx_mini_login_api(self):
        resp = self.client.post(
            '/api/auth/wx-mini/login/',
            {'code': 'mini-login-code'},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['code'], 200)
        self.assertIn('token', body['data'])
        token = body['data']['token']

        me_resp = self.client.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(me_resp.status_code, 200)

        resp2 = self.client.post(
            '/api/auth/wx-mini/login/',
            {'code': 'mini-login-code'},
            content_type='application/json',
        )
        self.assertEqual(resp2.json()['data']['user']['id'], body['data']['user']['id'])

    @override_settings(WECHAT_MOCK=True)
    def test_cross_platform_account_link_via_ticket_confirm(self):
        service = AuthService()
        mini = service.mini_program_login('shared-code-xyz')
        mini_user_id = mini['user']['id']

        ticket = service.create_login_ticket()
        service.confirm_login_ticket(ticket['ticket_id'], code='shared-code-xyz')
        poll = service.poll_login_ticket(ticket['ticket_id'])
        self.assertEqual(poll['user']['id'], mini_user_id)

    @override_settings(WECHAT_MOCK=True)
    def test_unauthenticated_me_returns_unauthorized(self):
        resp = self.client.get('/api/auth/me/')
        self.assertIn(resp.status_code, (401, 403))

    @override_settings(WECHAT_MOCK=True)
    def test_non_admin_cannot_list_users(self):
        user = User.objects.create_user(unionid='union_not_admin', nickname='普通')
        token = AuthService().issue_tokens(user)['token']
        resp = self.client.get('/api/admin/users/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(resp.status_code, 403)

    @override_settings(DEBUG=True)
    def test_dev_login_issues_real_jwt(self):
        User.objects.create_user(
            unionid='dev_pending_unionid',
            nickname='待审核商家',
            shop_status=User.ShopStatus.PENDING,
        )
        resp = self.client.post(
            '/api/auth/dev/login/',
            {'role': 'pending'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        token = resp.json()['data']['token']
        self.assertTrue(token.startswith('eyJ'))
        me_resp = self.client.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()['data']['shop_status'], User.ShopStatus.PENDING)

    def _login_as(self, user):
        service = AuthService()
        ticket = service.create_login_ticket()
        service.simulate_login_ticket(ticket['ticket_id'], user.id)
        poll = service.poll_login_ticket(ticket['ticket_id'])
        return poll['user'], poll['token']
