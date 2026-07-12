from typing import Optional

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.bikes.models import Bike
from apps.messaging.models import MessageItem, MessageThread
from apps.shops.models import Shop


class MessageServiceError(Exception):
    pass


def _format_datetime(dt) -> str:
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M')


def _bike_info(bike: Bike) -> str:
    return f'{bike.brand} {bike.model} {bike.year}年'


def _serialize_message(item: MessageItem) -> dict:
    return {
        'id': item.id,
        'sender_type': item.sender_type,
        'content': item.content,
        'created_at': _format_datetime(item.created_at),
    }


def serialize_thread(thread: MessageThread, *, include_messages: bool = True) -> dict:
    bike = thread.bike
    data = {
        'id': thread.id,
        'bike_id': thread.bike_id,
        'shop_id': thread.shop_id,
        'user_id': thread.user_id,
        'user_name': thread.user.nickname or f'用户{thread.user_id}',
        'bike_info': _bike_info(bike),
        'thread_status': thread.thread_status,
        'unread_count_user': thread.unread_count_user,
        'unread_count_shop': thread.unread_count_shop,
        'contact_phone': thread.contact_phone or '',
        'updated_at': _format_datetime(thread.last_message_at or thread.updated_at),
    }
    if include_messages:
        messages = thread.messages.filter(is_deleted=False).order_by('created_at')
        data['messages'] = [_serialize_message(m) for m in messages]
    return data


class MessageService:
    def list_user_threads(self, user: User) -> dict:
        threads = MessageThread.objects.filter(
            user=user,
            is_deleted=False,
        ).select_related('bike', 'user').prefetch_related('messages').order_by('-last_message_at', '-id')
        return {
            'list': [serialize_thread(t) for t in threads],
            'total': threads.count(),
        }

    def list_shop_threads(self, shop_id: int, status: Optional[int] = None) -> dict:
        qs = MessageThread.objects.filter(
            shop_id=shop_id,
            is_deleted=False,
        ).select_related('bike', 'user').prefetch_related('messages').order_by('-last_message_at', '-id')
        if status:
            qs = qs.filter(thread_status=status)
        threads = list(qs)
        return {
            'list': [serialize_thread(t) for t in threads],
            'total': len(threads),
        }

    def list_admin_threads(self) -> dict:
        threads = MessageThread.objects.filter(
            is_deleted=False,
        ).select_related('bike', 'user').prefetch_related('messages').order_by('-last_message_at', '-id')
        return {
            'list': [serialize_thread(t) for t in threads],
            'total': threads.count(),
        }

    def unread_count(self, user: User, role: str = 'user') -> dict:
        if role == 'shop':
            if not user.shop_id or user.shop_status != User.ShopStatus.APPROVED:
                return {'unread_count': 0, 'role': 'shop'}
            total = MessageThread.objects.filter(
                shop_id=user.shop_id,
                is_deleted=False,
            ).aggregate(total=Sum('unread_count_shop'))['total'] or 0
            return {'unread_count': int(total), 'role': 'shop'}
        total = MessageThread.objects.filter(
            user=user,
            is_deleted=False,
        ).aggregate(total=Sum('unread_count_user'))['total'] or 0
        return {'unread_count': int(total), 'role': 'user'}

    def get_thread(self, thread_id: int, user: User) -> dict:
        try:
            thread = MessageThread.objects.select_related('bike', 'user').prefetch_related('messages').get(
                pk=thread_id,
                is_deleted=False,
            )
        except MessageThread.DoesNotExist:
            raise MessageServiceError('会话不存在')
        self._ensure_thread_access(thread, user)
        return serialize_thread(thread)

    @transaction.atomic
    def create_or_append_thread(
        self,
        user: User,
        *,
        bike_id: int,
        content: str,
        contact_phone: str = '',
    ) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, is_deleted=False)
        except Bike.DoesNotExist:
            raise MessageServiceError('车辆不存在')
        thread = MessageThread.objects.filter(user=user, bike=bike, is_deleted=False).first()
        if thread:
            self._append_message(thread, user, MessageItem.SenderType.USER, content)
            thread.refresh_from_db()
            return serialize_thread(thread)
        now = timezone.now()
        thread = MessageThread.objects.create(
            shop=bike.shop,
            bike=bike,
            user=user,
            contact_phone=contact_phone or None,
            thread_status=MessageThread.ThreadStatus.UNREAD,
            unread_count_shop=1,
            unread_count_user=0,
            last_message_at=now,
            last_message_preview=content[:100],
        )
        MessageItem.objects.create(
            thread=thread,
            shop=bike.shop,
            sender_type=MessageItem.SenderType.USER,
            sender=user,
            content=content,
        )
        return serialize_thread(thread)

    @transaction.atomic
    def send_message(
        self,
        thread_id: int,
        sender: User,
        *,
        content: str,
        sender_type: int,
    ) -> dict:
        try:
            thread = MessageThread.objects.select_related('bike', 'user').get(
                pk=thread_id,
                is_deleted=False,
            )
        except MessageThread.DoesNotExist:
            raise MessageServiceError('会话不存在')
        self._ensure_thread_access(thread, sender, for_send=True, sender_type=sender_type)
        item = self._append_message(thread, sender, sender_type, content)
        return {
            'message': _serialize_message(item),
            'thread': serialize_thread(thread),
        }

    @transaction.atomic
    def mark_read(self, thread_id: int, user: User, role: str) -> dict:
        try:
            thread = MessageThread.objects.select_related('bike', 'user').prefetch_related('messages').get(
                pk=thread_id,
                is_deleted=False,
            )
        except MessageThread.DoesNotExist:
            raise MessageServiceError('会话不存在')
        self._ensure_thread_access(thread, user)
        now = timezone.now()
        if role == 'user':
            thread.unread_count_user = 0
            thread.user_read_at = now
        elif role == 'shop':
            thread.unread_count_shop = 0
            thread.shop_read_at = now
        else:
            raise MessageServiceError('无效的角色参数')
        thread.save(update_fields=['unread_count_user', 'unread_count_shop', 'user_read_at', 'shop_read_at', 'updated_at'])
        return serialize_thread(thread)

    def _append_message(
        self,
        thread: MessageThread,
        sender: User,
        sender_type: int,
        content: str,
    ) -> MessageItem:
        now = timezone.now()
        item = MessageItem.objects.create(
            thread=thread,
            shop=thread.shop,
            sender_type=sender_type,
            sender=sender,
            content=content,
        )
        thread.last_message_at = now
        thread.last_message_preview = content[:100]
        thread.updated_at = now
        if sender_type == MessageItem.SenderType.USER:
            thread.unread_count_shop = (thread.unread_count_shop or 0) + 1
            thread.thread_status = MessageThread.ThreadStatus.UNREAD
            thread.save(update_fields=[
                'last_message_at', 'last_message_preview', 'updated_at',
                'unread_count_shop', 'thread_status',
            ])
        else:
            thread.unread_count_user = (thread.unread_count_user or 0) + 1
            thread.thread_status = MessageThread.ThreadStatus.REPLIED
            thread.save(update_fields=[
                'last_message_at', 'last_message_preview', 'updated_at',
                'unread_count_user', 'thread_status',
            ])
        return item

    def _ensure_thread_access(
        self,
        thread: MessageThread,
        user: User,
        *,
        for_send: bool = False,
        sender_type: Optional[int] = None,
    ) -> None:
        if getattr(user, 'is_platform_admin', False):
            return
        if thread.user_id == user.id:
            if for_send and sender_type != MessageItem.SenderType.USER:
                raise MessageServiceError('无权以该身份发送消息')
            return
        if (
            user.shop_id
            and user.shop_id == thread.shop_id
            and user.shop_status == User.ShopStatus.APPROVED
        ):
            if for_send and sender_type != MessageItem.SenderType.SHOP:
                raise MessageServiceError('无权以该身份发送消息')
            return
        raise MessageServiceError('无权访问该会话')
