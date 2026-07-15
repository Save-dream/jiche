from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AuthLoginTicket, User
from apps.accounts.services.wechat import WeChatService, WeChatServiceError


class AuthService:
    def __init__(self):
        self.wechat = WeChatService()

    def issue_tokens(self, user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }

    def serialize_user(self, user: User) -> dict:
        return {
            'id': user.id,
            'nickname': user.nickname,
            'phone': user.phone,
            'avatar': user.avatar,
            'is_staff': user.is_staff,
            'is_super_staff': user.is_super_staff,
            'is_active': user.is_active,
            'is_deleted': user.is_deleted,
            'account_status': user.account_status,
            'shop_status': user.shop_status,
            'shop_id': user.shop_id,
            'ban_reason': user.ban_reason,
            'banned_at': user.banned_at.isoformat() if user.banned_at else None,
            'delete_reason': user.delete_reason,
            'deleted_at': user.deleted_at.isoformat() if user.deleted_at else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'last_login_platform': user.last_login_platform or '',
        }

    def _assert_not_platform_admin_target(self, target: User, action: str) -> None:
        """平台管理员（含预置超管与授权管理员）不可封禁/删除。"""
        if target.is_super_staff or target.is_staff:
            raise ValueError(f'平台管理员不可{action}')

    def password_register(
        self,
        *,
        username: str,
        password: str,
        nickname: str = '',
        phone: str | None = None,
    ) -> dict:
        """临时自助注册，等同微信授权后建号（正式环境将改回微信）。"""
        username = (username or '').strip()
        if User.objects.filter(internal_username=username, is_deleted=False).exists():
            raise ValueError('账号已存在')
        user = User.objects.create_user(
            internal_username=username,
            password=password,
            nickname=nickname or username,
            phone=phone or None,
            is_active=True,
            is_staff=False,
            is_super_staff=False,
        )
        self.update_login_meta(user, User.LoginPlatform.WEB)
        tokens = self.issue_tokens(user)
        return {
            'token': tokens['token'],
            'refresh_token': tokens['refresh_token'],
            'user': self.serialize_user(user),
        }

    def update_login_meta(self, user: User, platform: str) -> None:
        user.last_login_at = timezone.now()
        user.last_login_platform = platform
        user.save(update_fields=['last_login_at', 'last_login_platform', 'updated_at'])

    @transaction.atomic
    def get_or_create_wechat_user(
        self,
        *,
        mp_openid: str | None = None,
        web_openid: str | None = None,
        unionid: str | None = None,
        nickname: str = '',
        avatar: str | None = None,
        platform: str = User.LoginPlatform.WEB,
    ) -> User:
        user = None
        if unionid:
            user = User.objects.filter(unionid=unionid, is_deleted=False).first()
        if user is None and mp_openid:
            user = User.objects.filter(mp_openid=mp_openid, is_deleted=False).first()
        if user is None and web_openid:
            user = User.objects.filter(web_openid=web_openid, is_deleted=False).first()

        if user is None:
            user = User.objects.create_user(
                unionid=unionid,
                mp_openid=mp_openid,
                web_openid=web_openid,
                nickname=nickname or '微信用户',
                avatar=avatar,
            )
        else:
            fields = []
            if unionid and user.unionid != unionid:
                user.unionid = unionid
                fields.append('unionid')
            if mp_openid and user.mp_openid != mp_openid:
                user.mp_openid = mp_openid
                fields.append('mp_openid')
            if web_openid and user.web_openid != web_openid:
                user.web_openid = web_openid
                fields.append('web_openid')
            if nickname and not user.nickname:
                user.nickname = nickname
                fields.append('nickname')
            if avatar and not user.avatar:
                user.avatar = avatar
                fields.append('avatar')
            if fields:
                fields.append('updated_at')
                user.save(update_fields=fields)

        self.update_login_meta(user, platform)
        return user

    def mini_program_login(self, code: str) -> dict:
        try:
            session = self.wechat.code_to_session(code, platform='mini_program')
        except WeChatServiceError as exc:
            raise ValueError(str(exc)) from exc

        user = self.get_or_create_wechat_user(
            mp_openid=session.openid,
            unionid=session.unionid,
            platform=User.LoginPlatform.MINI_PROGRAM,
        )
        tokens = self.issue_tokens(user)
        return {'token': tokens['token'], 'user': self.serialize_user(user)}

    def create_login_ticket(self, *, redirect_path: str | None = None, client_ip: str | None = None) -> dict:
        ticket_id = f'T{uuid.uuid4().hex[:12].upper()}'
        expires_at = timezone.now() + timedelta(seconds=settings.LOGIN_TICKET_EXPIRE_SECONDS)
        ticket = AuthLoginTicket.objects.create(
            ticket=ticket_id,
            redirect_path=redirect_path,
            client_ip=client_ip,
            expires_at=expires_at,
        )
        return {
            'ticket_id': ticket.ticket,
            'status': ticket.status_label(),
            'qr_url': self.wechat.build_qr_placeholder_url(ticket.ticket),
            'expires_at': int(expires_at.timestamp() * 1000),
        }

    def get_ticket(self, ticket_id: str) -> AuthLoginTicket:
        try:
            ticket = AuthLoginTicket.objects.get(ticket=ticket_id)
        except AuthLoginTicket.DoesNotExist as exc:
            raise LookupError('登录票据不存在') from exc
        ticket.mark_expired_if_needed()
        return ticket

    def poll_login_ticket(self, ticket_id: str) -> dict:
        ticket = self.get_ticket(ticket_id)
        if ticket.status == AuthLoginTicket.Status.EXPIRED:
            return {'status': 'expired'}
        if ticket.status != AuthLoginTicket.Status.CONFIRMED or not ticket.user_id:
            return {'status': ticket.status_label()}

        tokens = self.issue_tokens(ticket.user)
        return {
            'status': 'confirmed',
            'token': tokens['token'],
            'user': self.serialize_user(ticket.user),
        }

    @transaction.atomic
    def confirm_login_ticket(
        self,
        ticket_id: str,
        *,
        code: str | None = None,
        mp_openid: str | None = None,
        unionid: str | None = None,
        web_openid: str | None = None,
    ) -> User:
        ticket = self.get_ticket(ticket_id)
        if ticket.status == AuthLoginTicket.Status.EXPIRED:
            raise ValueError('二维码已过期')
        if ticket.status == AuthLoginTicket.Status.CONFIRMED:
            return ticket.user

        if code:
            try:
                session = self.wechat.code_to_session(code, platform='mini_program')
            except WeChatServiceError as exc:
                raise ValueError(str(exc)) from exc
            mp_openid = session.openid
            unionid = session.unionid or unionid

        if not mp_openid and not web_openid and not unionid:
            raise ValueError('缺少微信身份信息')

        user = self.get_or_create_wechat_user(
            mp_openid=mp_openid,
            web_openid=web_openid,
            unionid=unionid,
            platform=User.LoginPlatform.WEB,
        )
        ticket.status = AuthLoginTicket.Status.CONFIRMED
        ticket.user = user
        ticket.scan_openid = web_openid or mp_openid
        ticket.scan_unionid = unionid
        ticket.confirmed_at = timezone.now()
        ticket.save(
            update_fields=[
                'status',
                'user',
                'scan_openid',
                'scan_unionid',
                'confirmed_at',
            ]
        )
        return user

    def simulate_login_ticket(self, ticket_id: str, user_id: int | None = None) -> User:
        if not settings.DEBUG:
            raise PermissionError('仅开发环境可用')

        if user_id:
            try:
                user = User.objects.get(id=user_id, is_deleted=False)
            except User.DoesNotExist as exc:
                raise LookupError('用户不存在') from exc
        else:
            user, _ = User.objects.get_or_create(
                unionid='dev_simulate_unionid',
                defaults={
                    'internal_username': 'dev_simulate_user',
                    'nickname': '开发测试用户',
                    'mp_openid': 'dev_mp_openid',
                },
            )

        ticket = self.get_ticket(ticket_id)
        if ticket.status == AuthLoginTicket.Status.EXPIRED:
            raise ValueError('二维码已过期')

        ticket.status = AuthLoginTicket.Status.SCANNED
        ticket.save(update_fields=['status'])

        ticket.status = AuthLoginTicket.Status.CONFIRMED
        ticket.user = user
        ticket.scan_openid = user.web_openid or user.mp_openid
        ticket.scan_unionid = user.unionid
        ticket.confirmed_at = timezone.now()
        ticket.save(
            update_fields=[
                'status',
                'user',
                'scan_openid',
                'scan_unionid',
                'confirmed_at',
            ]
        )
        return user

    def password_login(self, username: str, password: str) -> dict:
        username = (username or '').strip()
        if not username or not password:
            raise ValueError('请输入账号和密码')
        user = User.objects.filter(
            internal_username=username,
            is_deleted=False,
        ).first()
        if user is None or not user.check_password(password):
            raise ValueError('账号或密码错误')
        if not user.is_active:
            raise ValueError('账号已被封禁，无法登录')
        self.update_login_meta(user, User.LoginPlatform.WEB)
        tokens = self.issue_tokens(user)
        return {
            'token': tokens['token'],
            'refresh_token': tokens['refresh_token'],
            'user': self.serialize_user(user),
        }

    def grant_staff(self, operator: User, target: User) -> User:
        if not operator.is_platform_admin:
            raise PermissionError('需要管理员权限')
        if target.is_deleted or not target.is_active:
            raise ValueError('仅正常状态用户可授予管理员')
        target.is_staff = True
        target.staff_granted_by = operator
        target.staff_granted_at = timezone.now()
        target.save(update_fields=['is_staff', 'staff_granted_by', 'staff_granted_at', 'updated_at'])
        return target

    def revoke_staff(self, operator: User, target: User) -> User:
        if not operator.is_platform_admin:
            raise PermissionError('需要管理员权限')
        if target.is_super_staff:
            raise ValueError('预置超级管理员不可撤销')
        target.is_staff = False
        target.save(update_fields=['is_staff', 'updated_at'])
        return target

    def list_admin_users(self, status: str = 'active') -> dict:
        """
        status: active | banned | deleted | all
        默认仅正常用户；排序优先正常，再管理员。
        """
        qs = User.objects.all()
        status = (status or 'active').strip().lower()
        if status == 'active':
            qs = qs.filter(is_deleted=False, is_active=True)
        elif status == 'banned':
            qs = qs.filter(is_deleted=False, is_active=False)
        elif status == 'deleted':
            qs = qs.filter(is_deleted=True)
        elif status == 'all':
            pass
        else:
            raise ValueError('无效的状态筛选，可选：active / banned / deleted / all')

        qs = qs.order_by('is_deleted', '-is_active', '-is_super_staff', '-is_staff', '-id')
        users = list(qs)
        return {
            'list': [self.serialize_user(u) for u in users],
            'total': len(users),
            'status': status,
        }

    def ban_user(self, operator: User, target: User, reason: str) -> User:
        if not operator.is_platform_admin:
            raise PermissionError('需要管理员权限')
        if target.id == operator.id:
            raise ValueError('不能封禁自己')
        self._assert_not_platform_admin_target(target, '封禁')
        if target.is_deleted:
            raise ValueError('用户已删除')
        if not target.is_active:
            raise ValueError('用户已处于封禁状态')
        target.is_active = False
        target.banned_at = timezone.now()
        target.ban_reason = reason
        target.save(
            update_fields=[
                'is_active',
                'banned_at',
                'ban_reason',
                'updated_at',
            ]
        )
        return target

    def unban_user(self, operator: User, target: User) -> User:
        if not operator.is_platform_admin:
            raise PermissionError('需要管理员权限')
        if target.is_deleted:
            raise ValueError('已删除用户无法解封')
        if target.is_active:
            raise ValueError('用户未封禁')
        target.is_active = True
        target.banned_at = None
        target.ban_reason = None
        target.save(update_fields=['is_active', 'banned_at', 'ban_reason', 'updated_at'])
        return target

    def delete_user(self, operator: User, target: User, reason: str) -> User:
        """普通用户逻辑删除；平台管理员不可删。建议先封禁再删。"""
        if not operator.is_platform_admin:
            raise PermissionError('需要管理员权限')
        if target.id == operator.id:
            raise ValueError('不能删除自己')
        self._assert_not_platform_admin_target(target, '删除')
        if target.is_deleted:
            raise ValueError('用户已删除')
        target.is_deleted = True
        target.is_active = False
        target.deleted_at = timezone.now()
        target.delete_reason = reason
        target.save(
            update_fields=[
                'is_deleted',
                'is_active',
                'deleted_at',
                'delete_reason',
                'updated_at',
            ]
        )
        return target
