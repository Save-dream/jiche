from django.conf import settings
from django.db import models


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='用户',
    )
    bike = models.ForeignKey(
        'bikes.Bike',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='车源',
    )
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='商家',
    )
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        db_table = 'favorite'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = [('user', 'bike')]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'user={self.user_id} bike={self.bike_id}'
