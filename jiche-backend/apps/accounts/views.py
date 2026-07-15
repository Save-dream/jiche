from typing import Optional

from django.conf import settings
from rest_framework.views import APIView

from apps.accounts.permissions import IsAuthenticatedUser, IsPlatformAdmin
from apps.accounts.serializers import (
    LoginTicketConfirmSerializer,
    PasswordLoginSerializer,
    PasswordRegisterSerializer,
    ReasonActionSerializer,
    SimulateScanSerializer,
    UserPublicSerializer,
    WxMiniLoginSerializer,
)
from apps.accounts.services.auth_service import AuthService
from apps.common.response import error_response, success_response


def _client_ip(request) -> Optional[str]:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class WxMiniLoginView(APIView):
    """小程序 wx.login 登录。"""

    def post(self, request):
        serializer = WxMiniLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthService()
        try:
            data = service.mini_program_login(serializer.validated_data['code'])
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class CreateLoginTicketView(APIView):
    """Web 端创建扫码登录票据。"""

    def post(self, request):
        redirect_path = request.data.get('redirect_path')
        service = AuthService()
        data = service.create_login_ticket(
            redirect_path=redirect_path,
            client_ip=_client_ip(request),
        )
        return success_response(data)


class PollLoginTicketView(APIView):
    """轮询扫码登录状态。"""

    def get(self, request, ticket_id):
        service = AuthService()
        try:
            data = service.poll_login_ticket(ticket_id)
        except LookupError as exc:
            return error_response(str(exc), code=404)
        return success_response(data)


class ConfirmLoginTicketView(APIView):
    """小程序扫描 Web 二维码后确认登录。"""

    def post(self, request, ticket_id):
        serializer = LoginTicketConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthService()
        try:
            service.confirm_login_ticket(ticket_id, **serializer.validated_data)
        except LookupError as exc:
            return error_response(str(exc), code=404)
        except ValueError as exc:
            return error_response(str(exc), code=410)
        return success_response({'ok': True})


class SimulateScanLoginView(APIView):
    """开发环境模拟扫码成功。"""

    def post(self, request, ticket_id):
        if not settings.DEBUG:
            return error_response('仅开发环境可用', code=403, status=403)
        serializer = SimulateScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get('user_id')
        service = AuthService()
        try:
            service.simulate_login_ticket(ticket_id, user_id)
        except LookupError as exc:
            return error_response(str(exc), code=404)
        except ValueError as exc:
            return error_response(str(exc), code=410)
        return success_response({'ok': True})


class PasswordLoginView(APIView):
    """账号密码登录（临时替代微信扫码）。"""

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthService()
        try:
            data = service.password_login(
                serializer.validated_data['username'],
                serializer.validated_data['password'],
            )
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class PasswordRegisterView(APIView):
    """普通用户自助注册（微信未接通前的临时方案，注册即登录）。"""

    def post(self, request):
        serializer = PasswordRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthService()
        try:
            data = service.password_register(**serializer.validated_data)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class MeView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        serializer = UserPublicSerializer(request.user)
        return success_response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        # JWT 无状态，客户端删除 token 即可；预留服务端扩展点
        return success_response(None)


DEV_ROLE_UNIONIDS = {
    'user': 'placeholder_user_unionid',
    'pending': 'dev_pending_unionid',
    'shop': 'dev_shop_unionid',
    'banned': 'dev_banned_unionid',
    'admin': 'placeholder_admin_unionid',
}


class DevLoginView(APIView):
    """开发环境快速切换演示账号，签发真实 JWT。"""

    def post(self, request):
        if not settings.DEBUG:
            return error_response('仅开发环境可用', code=403, status=403)
        role = request.data.get('role')
        unionid = DEV_ROLE_UNIONIDS.get(role)
        if not unionid:
            return error_response('无效的开发角色', code=400)
        from apps.accounts.models import User

        try:
            user = User.objects.get(unionid=unionid, is_deleted=False, is_active=True)
        except User.DoesNotExist:
            return error_response(
                '演示账号未初始化，请先运行: python manage.py seed_auth_demo',
                code=404,
            )
        service = AuthService()
        tokens = service.issue_tokens(user)
        return success_response({
            'token': tokens['token'],
            'user': service.serialize_user(user),
        })


class AdminUserListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        status = request.query_params.get('status', 'active')
        service = AuthService()
        try:
            data = service.list_admin_users(status=status)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class GrantStaffView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id):
        from apps.accounts.models import User

        try:
            target = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        service = AuthService()
        try:
            target = service.grant_staff(request.user, target)
        except PermissionError as exc:
            return error_response(str(exc), code=403, status=403)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(service.serialize_user(target))


class RevokeStaffView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id):
        from apps.accounts.models import User

        try:
            target = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        service = AuthService()
        try:
            target = service.revoke_staff(request.user, target)
        except PermissionError as exc:
            return error_response(str(exc), code=403, status=403)
        except ValueError as exc:
            return error_response(str(exc), code=403, status=403)
        return success_response(service.serialize_user(target))


class BanUserView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id):
        from apps.accounts.models import User

        serializer = ReasonActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        service = AuthService()
        try:
            target = service.ban_user(request.user, target, serializer.validated_data['reason'])
        except PermissionError as exc:
            return error_response(str(exc), code=403, status=403)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(service.serialize_user(target))


class UnbanUserView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id):
        from apps.accounts.models import User

        try:
            target = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        service = AuthService()
        try:
            target = service.unban_user(request.user, target)
        except PermissionError as exc:
            return error_response(str(exc), code=403, status=403)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(service.serialize_user(target))


class DeleteUserView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id):
        from apps.accounts.models import User

        serializer = ReasonActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        service = AuthService()
        try:
            target = service.delete_user(request.user, target, serializer.validated_data['reason'])
        except PermissionError as exc:
            return error_response(str(exc), code=403, status=403)
        except ValueError as exc:
            return error_response(str(exc), code=400)
        return success_response(service.serialize_user(target))
