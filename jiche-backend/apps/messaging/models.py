from django.conf import settings
from django.db import models


class MessageThread(models.Model):
    class ThreadStatus(models.IntegerChoices):
        UNREAD = 1, '未读'
        READ_NO_REPLY = 2, '已读未回复'
        REPLIED = 3, '已回复'

    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='message_threads',
        verbose_name='商家',
    )
    bike = models.ForeignKey(
        'bikes.Bike',
        on_delete=models.CASCADE,
        related_name='message_threads',
        verbose_name='车源',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_threads',
        verbose_name='用户',
    )
    contact_phone = models.CharField('联系电话', max_length=11, null=True, blank=True)
    thread_status = models.SmallIntegerField(
        '会话状态',
        choices=ThreadStatus.choices,
        default=ThreadStatus.UNREAD,
    )
    unread_count_user = models.PositiveIntegerField('用户未读数', default=0)
    unread_count_shop = models.PositiveIntegerField('商家未读数', default=0)
    last_message_at = models.DateTimeField('最后消息时间', null=True, blank=True)
    last_message_preview = models.CharField('消息预览', max_length=100, null=True, blank=True)
    user_read_at = models.DateTimeField('用户已读时间', null=True, blank=True)
    shop_read_at = models.DateTimeField('商家已读时间', null=True, blank=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'message_thread'
        verbose_name = '咨询会话'
        verbose_name_plural = verbose_name
        unique_together = [('user', 'bike')]
        indexes = [
            models.Index(fields=['shop', 'thread_status', '-last_message_at']),
            models.Index(fields=['user', '-last_message_at']),
        ]

    def __str__(self):
        return f'thread#{self.id} bike={self.bike_id}'


class MessageItem(models.Model):
    class SenderType(models.IntegerChoices):
        USER = 1, '用户'
        SHOP = 2, '商家'
        SYSTEM = 3, '系统'

    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='会话',
    )
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='message_items',
        verbose_name='商家',
    )
    sender_type = models.SmallIntegerField('发送方', choices=SenderType.choices)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sent_messages',
        verbose_name='发送者',
    )
    content = models.CharField('消息内容', max_length=500)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        db_table = 'message_item'
        verbose_name = '会话消息'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['shop']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f'msg#{self.id} thread={self.thread_id}'
