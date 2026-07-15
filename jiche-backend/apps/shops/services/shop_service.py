from typing import Optional

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.bikes.models import Bike
from apps.bikes.services.bike_service import serialize_bike
from apps.bikes.services.sorting import filter_shop_bikes
from apps.messaging.models import MessageThread
from apps.shops.models import Shop, ShopApplication, UserShopVisit


class ShopServiceError(Exception):
    pass


def serialize_shop_public(shop: Shop) -> dict:
    bike_count = shop.bikes.filter(is_deleted=False).count()
    return {
        'id': shop.id,
        'name': shop.name,
        'contact_name': shop.contact_name,
        'phone': shop.phone,
        'address': shop.address,
        'main_models': shop.main_models,
        'shop_status': shop.shop_status,
        'avatar': shop.avatar or '',
        'bike_count': bike_count,
        'description': shop.description,
        'updated_at': shop.updated_at.strftime('%Y-%m-%d %H:%M:%S') if shop.updated_at else '',
    }


def serialize_shop_profile(shop: Shop) -> dict:
    data = serialize_shop_public(shop)
    data['shop_type'] = shop.get_shop_type_display()
    data['qualification_photo'] = shop.qualification_photo or ''
    data['created_at'] = shop.created_at.strftime('%Y-%m-%d') if shop.created_at else None
    return data


class ShopService:
    def get_shop_detail(self, shop_id: int, status: Optional[int] = None) -> dict:
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家不存在')
        if shop.is_deleted:
            raise ShopServiceError('店铺已注销，暂不可访问！')
        if shop.shop_status == Shop.ShopStatus.BANNED:
            raise ShopServiceError('店铺已封禁，暂不可访问！')
        bikes_qs = filter_shop_bikes(shop_id, c_end_only=True, status_filter=status)
        return {
            'shop': serialize_shop_public(shop),
            'bikes': [serialize_bike(b) for b in bikes_qs],
        }

    def get_merchant_profile(self, user: User) -> dict:
        shop = self._get_merchant_shop(user)
        return serialize_shop_profile(shop)

    @transaction.atomic
    def update_merchant_profile(self, user: User, data: dict) -> dict:
        shop = self._get_merchant_shop(user)
        allowed = [
            'name', 'contact_name', 'phone', 'address', 'main_models',
            'description', 'avatar', 'qualification_photo',
        ]
        for field in allowed:
            if field in data:
                setattr(shop, field, data[field])
        shop.save()
        return serialize_shop_profile(shop)

    def list_admin_shops(self) -> dict:
        shops = Shop.objects.filter(is_deleted=False).select_related('user').order_by('-id')
        result = []
        for shop in shops:
            item = serialize_shop_public(shop)
            item['user_id'] = shop.user_id
            item['user_name'] = shop.user.nickname or shop.contact_name
            result.append(item)
        return {'list': result, 'total': len(result)}

    @transaction.atomic
    def ban_shop(self, shop_id: int, reason: str = '') -> dict:
        try:
            shop = Shop.objects.select_related('user').get(pk=shop_id, is_deleted=False)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家不存在')
        shop.shop_status = Shop.ShopStatus.BANNED
        shop.banned_at = timezone.now()
        shop.ban_reason = reason or '违规封禁'
        shop.save(update_fields=['shop_status', 'banned_at', 'ban_reason', 'updated_at'])

        # 强制下架在售车源；已售/商家手动下架/违规下架不动
        now = timezone.now()
        Bike.objects.filter(
            shop_id=shop.id,
            is_deleted=False,
            bike_status=Bike.BikeStatus.ON_SALE,
        ).update(
            bike_status=Bike.BikeStatus.OFF_SHELF,
            off_shelf_at=now,
            offline_by_shop_ban=True,
            updated_at=now,
        )

        user = shop.user
        user.shop_status = User.ShopStatus.BANNED
        # 失效登录态：鉴权要求 is_active=True
        user.is_active = False
        user.save(update_fields=['shop_status', 'is_active', 'updated_at'])
        return serialize_shop_public(shop)

    @transaction.atomic
    def unban_shop(self, shop_id: int) -> dict:
        try:
            shop = Shop.objects.select_related('user').get(pk=shop_id, is_deleted=False)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家不存在')
        if shop.shop_status != Shop.ShopStatus.BANNED:
            raise ShopServiceError('商家未被封禁')
        shop.shop_status = Shop.ShopStatus.NORMAL
        shop.banned_at = None
        shop.ban_reason = None
        shop.save(update_fields=['shop_status', 'banned_at', 'ban_reason', 'updated_at'])

        # 仅恢复因封禁强制下架的车；商家手动下架不在此列
        now = timezone.now()
        Bike.objects.filter(
            shop_id=shop.id,
            is_deleted=False,
            offline_by_shop_ban=True,
        ).update(
            bike_status=Bike.BikeStatus.ON_SALE,
            offline_by_shop_ban=False,
            off_shelf_at=None,
            updated_at=now,
        )

        user = shop.user
        user.shop_status = User.ShopStatus.APPROVED
        user.is_active = True
        user.save(update_fields=['shop_status', 'is_active', 'updated_at'])
        return serialize_shop_public(shop)

    @transaction.atomic
    def soft_delete_shop(self, shop_id: int) -> dict:
        """商户逻辑删除：同步软删车源，释放手机号占用，解绑用户商家身份。"""
        try:
            shop = Shop.objects.select_related('user').get(pk=shop_id, is_deleted=False)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家不存在')

        data = serialize_shop_public(shop)
        was_shop_banned = shop.shop_status == Shop.ShopStatus.BANNED
        Bike.objects.filter(shop_id=shop.id, is_deleted=False).update(is_deleted=True)

        # 释放 unique phone，避免逻辑删除后占号
        shop.phone = f'D{shop.id:010d}'[:11]
        shop.is_deleted = True
        shop.save(update_fields=['phone', 'is_deleted', 'updated_at'])

        user = shop.user
        user.shop_status = User.ShopStatus.NORMAL
        user.shop_id = None
        update_fields = ['shop_status', 'shop_id', 'updated_at']
        # 店铺封禁会使账号 is_active=False；删除店铺后恢复为普通用户可登录
        if was_shop_banned and not user.is_active:
            user.is_active = True
            update_fields.append('is_active')
        user.save(update_fields=update_fields)
        data['is_deleted'] = True
        return data

    @transaction.atomic
    def record_visit(self, user: Optional[User], shop_id: int) -> dict:
        try:
            shop = Shop.objects.get(pk=shop_id, is_deleted=False, shop_status=Shop.ShopStatus.NORMAL)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家不存在')
        if user is None or not user.is_authenticated:
            return {'recorded': False}
        visit, created = UserShopVisit.objects.get_or_create(
            user=user,
            shop=shop,
            defaults={'visit_count': 1},
        )
        if not created:
            visit.visit_count += 1
            visit.last_visited_at = timezone.now()
            visit.save(update_fields=['visit_count', 'last_visited_at', 'updated_at'])
        return {
            'recorded': True,
            'shop_id': shop.id,
            'visit_count': visit.visit_count,
        }

    def list_user_visits(self, user: User, limit: int = 10) -> dict:
        visits = UserShopVisit.objects.filter(
            user=user,
        ).select_related('shop').order_by('-last_visited_at')[:limit]
        result = []
        for visit in visits:
            shop = visit.shop
            if shop.is_deleted or shop.shop_status == Shop.ShopStatus.BANNED:
                continue
            item = serialize_shop_public(shop)
            item['last_visited_at'] = visit.last_visited_at.strftime('%Y-%m-%d %H:%M')
            item['visit_count'] = visit.visit_count
            result.append(item)
        return {'list': result, 'total': len(result)}

    def get_shop_stats(self, shop_id: int) -> dict:
        bikes = Bike.objects.filter(shop_id=shop_id, is_deleted=False)
        unread = MessageThread.objects.filter(
            shop_id=shop_id,
            is_deleted=False,
        ).aggregate(total=Sum('unread_count_shop'))['total'] or 0
        return {
            'on_sale': bikes.filter(bike_status=Bike.BikeStatus.ON_SALE).count(),
            'sold': bikes.filter(bike_status=Bike.BikeStatus.SOLD).count(),
            'unread_messages': unread,
            'total_views': bikes.aggregate(total=Sum('view_count'))['total'] or 0,
        }

    def get_admin_stats(self) -> dict:
        return {
            'total_shops': Shop.objects.filter(is_deleted=False, shop_status=Shop.ShopStatus.NORMAL).count(),
            'pending_applications': ShopApplication.objects.filter(
                application_status=ShopApplication.ApplicationStatus.PENDING,
                is_deleted=False,
            ).count(),
            'total_bikes': Bike.objects.filter(is_deleted=False).count(),
            'total_messages': MessageThread.objects.filter(is_deleted=False).count(),
        }

    def _get_merchant_shop(self, user: User) -> Shop:
        if not user.shop_id:
            raise ShopServiceError('商家信息不存在')
        try:
            shop = Shop.objects.get(pk=user.shop_id, is_deleted=False)
        except Shop.DoesNotExist:
            raise ShopServiceError('商家信息不存在')
        if shop.shop_status == Shop.ShopStatus.BANNED:
            raise ShopServiceError('店铺已封禁，暂不可访问！')
        return shop
