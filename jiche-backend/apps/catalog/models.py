from django.db import models


class Brand(models.Model):
    name = models.CharField('品牌名称', max_length=32, unique=True)
    sort_order = models.IntegerField('排序权重', default=0)
    is_enabled = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class BrandModel(models.Model):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name='品牌',
    )
    name = models.CharField('车型名称', max_length=64)
    is_enabled = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'brand_model'
        verbose_name = '车型'
        verbose_name_plural = verbose_name
        unique_together = [('brand', 'name')]
        indexes = [
            models.Index(fields=['brand']),
        ]
        ordering = ['id']

    def __str__(self):
        return f'{self.brand.name} {self.name}'
