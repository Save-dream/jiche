from django.db import models


class Bike(models.Model):
    class BikeStatus(models.IntegerChoices):
        ON_SALE = 1, '在售'
        SOLD = 2, '已售'
        OFF_SHELF = 3, '商家下架'
        FORCE_OFF = 4, '违规下架'

    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.PROTECT,
        related_name='bikes',
        verbose_name='所属商家',
    )
    brand_id = models.IntegerField('品牌 ID', null=True, blank=True)
    brand = models.CharField('品牌名称', max_length=32)
    model = models.CharField('车型', max_length=64)
    year = models.SmallIntegerField('上牌年份')
    register_date = models.DateField('上牌日期', null=True, blank=True)
    displacement = models.CharField('排量', max_length=16)
    mileage = models.PositiveIntegerField('行驶里程', default=0)
    transfer_count = models.PositiveSmallIntegerField('过户次数', default=0)
    price = models.DecimalField('售价', max_digits=12, decimal_places=2)
    can_transfer = models.BooleanField('是否可过户', default=True)
    negotiable = models.BooleanField('是否可议价', default=True)
    engine_status = models.CharField('发动机状态', max_length=500)
    suspension_status = models.CharField('减震状态', max_length=500)
    brake_status = models.CharField('刹车状态', max_length=500)
    electrical_status = models.CharField('电控状态', max_length=500)
    frame_status = models.CharField('车架状态', max_length=500)
    modification = models.CharField('改装明细', max_length=500)
    defects = models.CharField('瑕疵说明', max_length=500)
    maintenance = models.CharField('维保记录', max_length=500)
    delivery_method = models.CharField('交付方式', max_length=64, blank=True, default='')
    fee_note = models.CharField('费用说明', max_length=200, blank=True, default='')
    after_sale = models.CharField('售后说明', max_length=200, blank=True, default='')
    cover_image = models.CharField('封面图', max_length=512)
    bike_status = models.SmallIntegerField(
        '车辆状态',
        choices=BikeStatus.choices,
        default=BikeStatus.ON_SALE,
    )
    view_count = models.PositiveIntegerField('浏览次数', default=0)
    published_at = models.DateTimeField('首次上架时间', null=True, blank=True)
    off_shelf_at = models.DateTimeField('下架时间', null=True, blank=True)
    force_off_reason = models.CharField('违规下架原因', max_length=200, null=True, blank=True)
    force_off_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='force_off_bikes',
        verbose_name='违规操作人',
    )
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'bike'
        verbose_name = '车源'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['shop', 'bike_status', '-published_at']),
            models.Index(fields=['shop', 'is_deleted']),
            models.Index(fields=['price']),
            models.Index(fields=['year']),
        ]

    def __str__(self):
        return f'{self.brand} {self.model} ({self.year})'


class ShareLink(models.Model):
    short_code = models.CharField('短链码', max_length=16, unique=True)
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='share_links',
        verbose_name='商家',
    )
    bike = models.ForeignKey(
        Bike,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='share_links',
        verbose_name='车源',
    )
    timestamp = models.BigIntegerField('签名时间戳')
    sign = models.CharField('HMAC 签名', max_length=128)
    expired_at = models.DateTimeField('过期时间')
    click_count = models.PositiveIntegerField('点击次数', default=0)
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_share_links',
        verbose_name='创建人',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'share_link'
        verbose_name = '分享短链'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['shop', 'bike']),
            models.Index(fields=['expired_at']),
        ]

    def __str__(self):
        return self.short_code


class BikeMedia(models.Model):
    class MediaType(models.IntegerChoices):
        COVER = 1, '封面'
        DISPLAY = 2, '展示图'
        CONDITION = 3, '车况图'
        VIDEO = 4, '视频'

    bike = models.ForeignKey(
        Bike,
        on_delete=models.CASCADE,
        related_name='media_items',
        verbose_name='车源',
    )
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='bike_media',
        verbose_name='商家',
    )
    media_type = models.SmallIntegerField('媒体类型', choices=MediaType.choices)
    url = models.CharField('媒体 URL', max_length=512)
    sort_order = models.IntegerField('排序', default=0)
    duration = models.IntegerField('视频时长', null=True, blank=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'bike_media'
        verbose_name = '车源媒体'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['bike', 'media_type', 'sort_order']),
            models.Index(fields=['shop']),
        ]

    def __str__(self):
        return f'{self.bike_id} type={self.media_type}'
