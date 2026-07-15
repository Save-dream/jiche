from __future__ import annotations

from typing import Optional

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services.auth_service import AuthService
from apps.shops.models import Shop, ShopApplication


SHOP_TYPE_LABELS = {
    ShopApplication.ShopType.PERSONAL: '个人商户',
    ShopApplication.ShopType.ENTERPRISE: '企业商户',
}

LABEL_TO_SHOP_TYPE = {v: k for k, v in SHOP_TYPE_LABELS.items()}


class ApplicationServiceError(Exception):
    pass


class ApplicationService:
    def _serialize_application(self, application: ShopApplication) -> dict:
        return {
            'id': application.id,
            'user_id': application.user_id,
            'user_name': application.user.nickname or application.contact_name,
            'name': application.name or '',
            'shop_type': application.shop_type_label,
            'contact_name': application.contact_name,
            'phone': application.phone,
            'address': application.address,
            'main_models': application.main_models,
            'description': application.description,
            'qualification_photo': application.qualification_photo or '',
            'shop_status': application.application_status,
            'application_status': application.application_status,
            'applied_at': application.applied_at.strftime('%Y-%m-%d %H:%M'),
            'reject_reason': application.reject_reason or '',
        }

    def _parse_shop_type(self, value) -> int:
        if isinstance(value, int):
            return value
        if value in LABEL_TO_SHOP_TYPE:
            return LABEL_TO_SHOP_TYPE[value]
        raise ApplicationServiceError('无效的入驻类型')

    def _validate_can_apply(self, user: User) -> None:
        if user.shop_status == User.ShopStatus.PENDING:
            raise ApplicationServiceError('申请审核中，请勿重复提交')
        if user.shop_status == User.ShopStatus.APPROVED:
            raise ApplicationServiceError('您已是入驻商家，无需重复申请')
        if user.shop_status == User.ShopStatus.BANNED:
            raise ApplicationServiceError('账号已封禁，无法提交入驻申请')

    def _validate_phone_available(self, user: User, phone: str) -> None:
        if Shop.objects.filter(phone=phone, is_deleted=False).exclude(user=user).exists():
            raise ApplicationServiceError('该联系电话已被其他商家使用')
        pending_exists = ShopApplication.objects.filter(
            phone=phone,
            application_status=ShopApplication.ApplicationStatus.PENDING,
            is_deleted=False,
        ).exclude(user=user).exists()
        if pending_exists:
            raise ApplicationServiceError('该联系电话已有待审核申请')

    @transaction.atomic
    def submit_application(self, user: User, data: dict) -> dict:
        self._validate_can_apply(user)
        shop_type = self._parse_shop_type(data['shop_type'])
        phone = data['phone']
        self._validate_phone_available(user, phone)

        if shop_type == ShopApplication.ShopType.ENTERPRISE and not data.get('qualification_photo'):
            raise ApplicationServiceError('企业商户必须上传资质照片')
        shop_name = (data.get('name') or '').strip()
        if not shop_name:
            raise ApplicationServiceError('请填写商家名称')

        application = ShopApplication.objects.create(
            user=user,
            name=shop_name[:64],
            shop_type=shop_type,
            contact_name=data['contact_name'],
            phone=phone,
            address=data.get('address', ''),
            main_models=data.get('main_models', ''),
            description=data.get('description', ''),
            wechat_qrcode='',
            qualification_photo=data.get('qualification_photo') or None,
            application_status=ShopApplication.ApplicationStatus.PENDING,
        )
        user.shop_status = User.ShopStatus.PENDING
        user.save(update_fields=['shop_status', 'updated_at'])

        return {
            'application': self._serialize_application(application),
            'user': AuthService().serialize_user(user),
        }

    def get_my_application(self, user: User) -> Optional[dict]:
        queryset = ShopApplication.objects.filter(user=user, is_deleted=False).select_related('user')
        if user.shop_status == User.ShopStatus.PENDING:
            application = queryset.filter(
                application_status=ShopApplication.ApplicationStatus.PENDING,
            ).order_by('-applied_at').first()
        else:
            application = queryset.order_by('-applied_at').first()
        if not application:
            return None
        return self._serialize_application(application)

    def list_applications(self, *, status: Optional[int] = None) -> dict:
        queryset = ShopApplication.objects.filter(is_deleted=False).select_related('user')
        if status:
            queryset = queryset.filter(application_status=status)
        applications = list(queryset.order_by('-applied_at'))
        return {
            'list': [self._serialize_application(item) for item in applications],
            'total': len(applications),
        }

    def _generate_shop_name(self, application: ShopApplication) -> str:
        base = f'{application.contact_name}的二手摩托'
        return base[:64]

    @transaction.atomic
    def audit_application(
        self,
        *,
        application_id: int,
        auditor: User,
        action: str,
        reject_reason: str = '',
    ) -> dict:
        try:
            application = ShopApplication.objects.select_for_update().select_related('user').get(
                id=application_id,
                is_deleted=False,
            )
        except ShopApplication.DoesNotExist as exc:
            raise ApplicationServiceError('申请不存在') from exc

        if application.application_status != ShopApplication.ApplicationStatus.PENDING:
            raise ApplicationServiceError('该申请已处理')

        user = application.user
        now = timezone.now()

        if action == 'approve':
            shop = self._approve_create_or_revive_shop(application, user, now)
            application.application_status = ShopApplication.ApplicationStatus.APPROVED
            user.shop_status = User.ShopStatus.APPROVED
            user.shop_id = shop.id
        elif action == 'reject':
            if not reject_reason:
                raise ApplicationServiceError('请填写驳回原因')
            application.application_status = ShopApplication.ApplicationStatus.REJECTED
            application.reject_reason = reject_reason
            user.shop_status = User.ShopStatus.REJECTED
        else:
            raise ApplicationServiceError('无效审核操作')

        application.audited_by = auditor
        application.audited_at = now
        try:
            application.save()
            user.save(update_fields=['shop_status', 'shop_id', 'updated_at'])
        except IntegrityError as exc:
            raise ApplicationServiceError(f'审核写入失败：{exc}') from exc

        return {
            'application': self._serialize_application(application),
            'user': AuthService().serialize_user(user),
        }

    def _approve_create_or_revive_shop(
        self,
        application: ShopApplication,
        user: User,
        now,
    ) -> Shop:
        """创建商家；若该用户已有逻辑删除店铺则复活并更新资料。"""
        # 锁定用户行，避免并发审核撞 OneToOne
        user = User.objects.select_for_update().get(pk=user.pk)

        active = Shop.objects.filter(user=user, is_deleted=False).first()
        if active:
            raise ApplicationServiceError('该用户已是商家')

        phone = (application.phone or '').strip()
        if not phone:
            raise ApplicationServiceError('申请缺少联系电话，无法通过')

        phone_taken = (
            Shop.objects.filter(phone=phone, is_deleted=False)
            .exclude(user=user)
            .exists()
        )
        if phone_taken:
            raise ApplicationServiceError('联系电话已被占用')

        name = (application.name or self._generate_shop_name(application)).strip()[:64]
        if not name:
            name = self._generate_shop_name(application)[:64]

        # 截断到模型字段长度，避免 MySQL DataError 变成未捕获 500
        fields = {
            'name': name[:64],
            'shop_type': application.shop_type,
            'contact_name': (application.contact_name or '')[:32],
            'phone': phone[:11],
            'address': (application.address or '')[:100],
            'main_models': (application.main_models or '')[:50],
            'description': (application.description or '')[:200],
            'wechat_qrcode': '',
            'qualification_photo': (
                (application.qualification_photo[:512] if application.qualification_photo else None)
            ),
            'shop_status': Shop.ShopStatus.NORMAL,
            'approved_at': now,
            'banned_at': None,
            'ban_reason': None,
            'is_deleted': False,
        }

        existing = Shop.objects.filter(user=user).first()
        try:
            if existing:
                for key, value in fields.items():
                    setattr(existing, key, value)
                existing.save()
                return existing
            return Shop.objects.create(user=user, **fields)
        except IntegrityError as exc:
            raise ApplicationServiceError(
                '创建商家失败，可能是联系电话或用户店铺关系冲突，请检查后重试'
            ) from exc
        except Exception as exc:
            raise ApplicationServiceError(f'创建商家失败：{exc}') from exc
