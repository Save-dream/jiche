import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, internal_username=None, password=None, **extra_fields):
        if not internal_username:
            internal_username = f'u_{uuid.uuid4().hex[:16]}'
        user = self.model(internal_username=internal_username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_super_admin(self, unionid, nickname='平台管理员', phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_super_staff', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(
            internal_username=f'admin_{unionid[:16]}',
            password=password,
            unionid=unionid,
            nickname=nickname,
            phone=phone,
            **extra_fields,
        )


class User(AbstractBaseUser):
    class ShopStatus(models.IntegerChoices):
        NORMAL = 0, '普通用户'
        PENDING = 1, '待审核'
        APPROVED = 2, '已入驻'
        REJECTED = 3, '审核驳回'
        BANNED = 4, '已封禁'

    class LoginPlatform(models.TextChoices):
        MINI_PROGRAM = 'mini_program', '小程序'
        WEB = 'web', 'Web'

    internal_username = models.CharField('内部用户名', max_length=64, unique=True)
    unionid = models.CharField('微信 unionid', max_length=64, null=True, blank=True, unique=True)
    mp_openid = models.CharField('小程序 openid', max_length=64, null=True, blank=True, unique=True)
    web_openid = models.CharField('Web openid', max_length=64, null=True, blank=True, unique=True)
    nickname = models.CharField('昵称', max_length=64, blank=True, default='')
    phone = models.CharField('手机号', max_length=11, null=True, blank=True)
    avatar = models.URLField('头像', max_length=512, null=True, blank=True)
    is_staff = models.BooleanField('平台管理员', default=False)
    is_super_staff = models.BooleanField('预置超级管理员', default=False)
    staff_granted_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='granted_staff_users',
        verbose_name='授权人',
    )
    staff_granted_at = models.DateTimeField('授权时间', null=True, blank=True)
    shop_status = models.SmallIntegerField(
        '商家状态',
        choices=ShopStatus.choices,
        default=ShopStatus.NORMAL,
    )
    shop_id = models.BigIntegerField('关联商家 ID', null=True, blank=True)
    last_login_at = models.DateTimeField('最近登录时间', null=True, blank=True)
    last_login_platform = models.CharField(
        '最近登录平台',
        max_length=16,
        blank=True,
        default='',
        choices=LoginPlatform.choices,
    )
    is_deleted = models.BooleanField('逻辑删除', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    banned_at = models.DateTimeField('封禁时间', null=True, blank=True)
    ban_reason = models.CharField('封禁原因', max_length=200, null=True, blank=True)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)
    delete_reason = models.CharField('删除原因', max_length=200, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'internal_username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['shop_status']),
            models.Index(fields=['shop_id']),
            models.Index(fields=['is_staff']),
        ]

    def __str__(self):
        return self.nickname or self.internal_username

    @property
    def is_platform_admin(self):
        return self.is_staff and self.is_active and not self.is_deleted

    @property
    def account_status(self) -> str:
        """账户生命周期状态：active / banned / deleted。"""
        if self.is_deleted:
            return 'deleted'
        if not self.is_active:
            return 'banned'
        return 'active'


class AuthLoginTicket(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, '待扫码'
        SCANNED = 1, '已扫码待确认'
        CONFIRMED = 2, '已确认'
        EXPIRED = 3, '已过期'

    ticket = models.CharField('票据', max_length=64, unique=True)
    status = models.SmallIntegerField('状态', choices=Status.choices, default=Status.PENDING)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='login_tickets',
        verbose_name='登录用户',
    )
    scan_openid = models.CharField('扫码 openid', max_length=64, null=True, blank=True)
    scan_unionid = models.CharField('扫码 unionid', max_length=64, null=True, blank=True)
    redirect_path = models.CharField('跳转路径', max_length=256, null=True, blank=True)
    client_ip = models.GenericIPAddressField('客户端 IP', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间')
    confirmed_at = models.DateTimeField('确认时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'auth_login_ticket'
        verbose_name = '扫码登录票据'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['status', 'expires_at']),
        ]

    def __str__(self):
        return self.ticket

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_expired_if_needed(self):
        if self.is_expired and self.status != self.Status.CONFIRMED:
            self.status = self.Status.EXPIRED
            self.save(update_fields=['status'])
            return True
        return self.status == self.Status.EXPIRED

    def status_label(self):
        mapping = {
            self.Status.PENDING: 'pending',
            self.Status.SCANNED: 'scanned',
            self.Status.CONFIRMED: 'confirmed',
            self.Status.EXPIRED: 'expired',
        }
        return mapping.get(self.status, 'pending')
