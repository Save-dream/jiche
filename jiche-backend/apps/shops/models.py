from django.conf import settings
from django.db import models


class Shop(models.Model):
    class ShopType(models.IntegerChoices):
        PERSONAL = 1, '个人商户'
        ENTERPRISE = 2, '企业商户'

    class ShopStatus(models.IntegerChoices):
        NORMAL = 2, '正常'
        BANNED = 4, '封禁'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='shop',
        verbose_name='商家主账号',
    )
    name = models.CharField('商家名称', max_length=64)
    shop_type = models.SmallIntegerField('入驻类型', choices=ShopType.choices)
    contact_name = models.CharField('联系人', max_length=32)
    phone = models.CharField('联系电话', max_length=11, unique=True)
    address = models.CharField('经营地址', max_length=100, blank=True, default='')
    main_models = models.CharField('主营车型', max_length=50, blank=True, default='')
    description = models.CharField('商家简介', max_length=200, blank=True, default='')
    avatar = models.CharField('店铺头像', max_length=512, null=True, blank=True)
    wechat_qrcode = models.CharField('微信二维码', max_length=512)
    qualification_photo = models.CharField('资质照片', max_length=512, null=True, blank=True)
    shop_status = models.SmallIntegerField(
        '商家状态',
        choices=ShopStatus.choices,
        default=ShopStatus.NORMAL,
    )
    approved_at = models.DateTimeField('审核通过时间', null=True, blank=True)
    banned_at = models.DateTimeField('封禁时间', null=True, blank=True)
    ban_reason = models.CharField('封禁原因', max_length=200, null=True, blank=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'shop'
        verbose_name = '商家'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['shop_status']),
        ]

    def __str__(self):
        return self.name


class ShopApplication(models.Model):
    class ShopType(models.IntegerChoices):
        PERSONAL = 1, '个人商户'
        ENTERPRISE = 2, '企业商户'

    class ApplicationStatus(models.IntegerChoices):
        PENDING = 1, '待审核'
        APPROVED = 2, '已通过'
        REJECTED = 3, '已驳回'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop_applications',
        verbose_name='申请人',
    )
    name = models.CharField('商家名称', max_length=64, blank=True, default='')
    shop_type = models.SmallIntegerField('入驻类型', choices=ShopType.choices)
    contact_name = models.CharField('联系人', max_length=32)
    phone = models.CharField('联系电话', max_length=11)
    address = models.CharField('经营地址', max_length=100, blank=True, default='')
    main_models = models.CharField('主营车型', max_length=50, blank=True, default='')
    description = models.CharField('入驻说明', max_length=200, blank=True, default='')
    wechat_qrcode = models.CharField('微信二维码', max_length=512)
    qualification_photo = models.CharField('资质照片', max_length=512, null=True, blank=True)
    application_status = models.SmallIntegerField(
        '申请状态',
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    reject_reason = models.CharField('驳回原因', max_length=200, null=True, blank=True)
    audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audited_applications',
        verbose_name='审核人',
    )
    audited_at = models.DateTimeField('审核时间', null=True, blank=True)
    applied_at = models.DateTimeField('申请时间', auto_now_add=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'shop_application'
        verbose_name = '商家入驻申请'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['application_status']),
            models.Index(fields=['-applied_at']),
        ]
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.contact_name}({self.get_application_status_display()})'

    @property
    def shop_type_label(self):
        return self.get_shop_type_display()


class UserShopVisit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop_visits',
        verbose_name='用户',
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name='商家',
    )
    visit_count = models.PositiveIntegerField('访问次数', default=1)
    last_visited_at = models.DateTimeField('最近访问时间', auto_now=True)
    created_at = models.DateTimeField('首次访问时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'user_shop_visit'
        verbose_name = '商家访问记录'
        verbose_name_plural = verbose_name
        unique_together = [('user', 'shop')]
        indexes = [
            models.Index(fields=['user', '-last_visited_at']),
        ]

    def __str__(self):
        return f'user={self.user_id} shop={self.shop_id}'
