from typing import List, Optional

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.accounts.models import User
from apps.bikes.models import Bike, BikeMedia
from apps.bikes.services.sorting import apply_bike_sorting, filter_shop_bikes
from apps.shops.models import Shop


class BikeServiceError(Exception):
    pass


def _format_date(dt) -> Optional[str]:
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d')


def _format_datetime(dt) -> Optional[str]:
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d %H:%M')


def _media_urls(bike: Bike, media_type: int) -> List[str]:
    return list(
        bike.media_items.filter(
            media_type=media_type,
            is_deleted=False,
        ).order_by('sort_order', 'id').values_list('url', flat=True)
    )


def serialize_bike(bike: Bike, *, include_shop_name: bool = True) -> dict:
    data = {
        'id': bike.id,
        'shop_id': bike.shop_id,
        'brand': bike.brand,
        'model': bike.model,
        'year': bike.year,
        'displacement': bike.displacement,
        'mileage': bike.mileage,
        'price': float(bike.price),
        'can_transfer': bike.can_transfer,
        'negotiable': bike.negotiable,
        'bike_status': bike.bike_status,
        'cover_image': bike.cover_image,
        'images': _media_urls(bike, BikeMedia.MediaType.DISPLAY),
        'condition_images': _media_urls(bike, BikeMedia.MediaType.CONDITION),
        'engine_status': bike.engine_status,
        'suspension_status': bike.suspension_status,
        'brake_status': bike.brake_status,
        'electrical_status': bike.electrical_status,
        'frame_status': bike.frame_status,
        'modification': bike.modification,
        'defects': bike.defects,
        'maintenance': bike.maintenance,
        'delivery_method': bike.delivery_method,
        'after_sale': bike.after_sale,
        'fee_note': bike.fee_note,
        'published_at': _format_date(bike.published_at),
        'created_at': _format_date(bike.created_at),
        'is_deleted': 1 if bike.is_deleted else 0,
        'view_count': bike.view_count,
    }
    if include_shop_name:
        shop_name = bike.shop.name if hasattr(bike, 'shop') and bike.shop else ''
        data['shop_name'] = shop_name
    return data


def serialize_shop_for_bike_detail(shop: Shop) -> dict:
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


class BikeService:
    def get_bike_detail(
        self,
        bike_id: int,
        shop_id: Optional[int] = None,
        *,
        timestamp: Optional[str] = None,
        sign: Optional[str] = None,
    ) -> dict:
        from apps.bikes.services.share_service import ShareService, ShareServiceError

        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在或已删除')
        shop = bike.shop
        if shop.is_deleted:
            raise BikeServiceError('店铺已注销，暂不可访问！')
        if shop.shop_status == Shop.ShopStatus.BANNED:
            raise BikeServiceError('店铺已封禁，暂不可访问！')
        if bike.is_deleted:
            raise BikeServiceError('车辆不存在或已删除')
        if bike.bike_status not in (Bike.BikeStatus.ON_SALE, Bike.BikeStatus.SOLD):
            raise BikeServiceError('车辆不存在或已删除')
        if shop_id is None:
            raise BikeServiceError('无权查看该商家商品')
        if bike.shop_id != shop_id:
            raise BikeServiceError('无权查看该商家商品')
        # 带来源签名时必须验签（分享链）；站内跳转仅校验 shop_id
        if timestamp or sign:
            try:
                ShareService().verify_sign(shop_id, bike_id, timestamp, sign)
            except ShareServiceError as exc:
                raise BikeServiceError(str(exc)) from exc
        Bike.objects.filter(pk=bike_id).update(view_count=F('view_count') + 1)
        bike.refresh_from_db()
        data = serialize_bike(bike)
        data['shop'] = serialize_shop_for_bike_detail(bike.shop)
        return data

    def list_merchant_bikes(self, shop_id: int, status: Optional[int] = None) -> dict:
        qs = filter_shop_bikes(shop_id, status_filter=status)
        bikes = list(qs)
        return {
            'list': [serialize_bike(b) for b in bikes],
            'total': len(bikes),
        }

    def list_admin_bikes(self) -> dict:
        qs = apply_bike_sorting(
            Bike.objects.select_related('shop').filter(is_deleted=False)
        )
        bikes = list(qs)
        return {
            'list': [serialize_bike(b) for b in bikes],
            'total': len(bikes),
        }

    def get_merchant_bike(self, shop: Shop, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        return serialize_bike(bike)

    @transaction.atomic
    def create_bike(self, shop: Shop, data: dict) -> dict:
        bike = self._build_bike(shop, data)
        bike.bike_status = Bike.BikeStatus.ON_SALE
        bike.published_at = timezone.now()
        bike.save()
        self._sync_media(bike, data)
        bike.refresh_from_db()
        return serialize_bike(bike)

    @transaction.atomic
    def update_bike(self, shop: Shop, bike_id: int, data: dict) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        if bike.bike_status == Bike.BikeStatus.FORCE_OFF:
            raise BikeServiceError('违规下架车辆不可编辑，请联系平台管理员')
        self._apply_bike_fields(bike, data)
        bike.save()
        if any(k in data for k in ('cover_image', 'images', 'condition_images')):
            self._sync_media(bike, data)
        bike.refresh_from_db()
        return serialize_bike(bike)

    @transaction.atomic
    def off_shelf_bike(self, shop: Shop, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        if bike.bike_status == Bike.BikeStatus.FORCE_OFF:
            raise BikeServiceError('违规下架车辆不可操作')
        bike.bike_status = Bike.BikeStatus.OFF_SHELF
        bike.off_shelf_at = timezone.now()
        bike.save(update_fields=['bike_status', 'off_shelf_at', 'updated_at'])
        return serialize_bike(bike)

    @transaction.atomic
    def on_shelf_bike(self, shop: Shop, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        if bike.bike_status == Bike.BikeStatus.FORCE_OFF:
            raise BikeServiceError('违规下架车辆不可操作，请联系平台管理员')
        if bike.bike_status != Bike.BikeStatus.OFF_SHELF:
            raise BikeServiceError('仅已下架车辆可重新上架')
        bike.bike_status = Bike.BikeStatus.ON_SALE
        if not bike.published_at:
            bike.published_at = timezone.now()
        bike.save(update_fields=['bike_status', 'published_at', 'updated_at'])
        return serialize_bike(bike)

    @transaction.atomic
    def mark_sold_bike(self, shop: Shop, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        if bike.bike_status == Bike.BikeStatus.FORCE_OFF:
            raise BikeServiceError('违规下架车辆不可操作')
        if bike.bike_status == Bike.BikeStatus.SOLD:
            return serialize_bike(bike)
        if bike.bike_status not in (Bike.BikeStatus.ON_SALE, Bike.BikeStatus.OFF_SHELF):
            raise BikeServiceError('当前状态不可标记已售')
        bike.bike_status = Bike.BikeStatus.SOLD
        bike.save(update_fields=['bike_status', 'updated_at'])
        return serialize_bike(bike)

    @transaction.atomic
    def delete_bike(self, shop: Shop, bike_id: int) -> None:
        try:
            bike = Bike.objects.get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        bike.is_deleted = True
        bike.save(update_fields=['is_deleted', 'updated_at'])

    @transaction.atomic
    def force_off_shelf(self, bike_id: int, admin: User, reason: str = '') -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        bike.bike_status = Bike.BikeStatus.FORCE_OFF
        bike.off_shelf_at = timezone.now()
        bike.force_off_reason = reason or '违规下架'
        bike.force_off_by = admin
        bike.save(update_fields=[
            'bike_status', 'off_shelf_at', 'force_off_reason', 'force_off_by', 'updated_at',
        ])
        return serialize_bike(bike)

    @transaction.atomic
    def restore_bike(self, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        if bike.bike_status != Bike.BikeStatus.FORCE_OFF:
            raise BikeServiceError('仅违规下架车辆可恢复')
        bike.bike_status = Bike.BikeStatus.ON_SALE
        bike.force_off_reason = None
        bike.force_off_by = None
        if not bike.published_at:
            bike.published_at = timezone.now()
        bike.save(update_fields=[
            'bike_status', 'force_off_reason', 'force_off_by', 'published_at', 'updated_at',
        ])
        return serialize_bike(bike)

    @transaction.atomic
    def admin_delete_bike(self, bike_id: int) -> None:
        try:
            bike = Bike.objects.get(pk=bike_id, is_deleted=False)
        except Bike.DoesNotExist:
            raise BikeServiceError('车辆不存在')
        bike.is_deleted = True
        bike.save(update_fields=['is_deleted', 'updated_at'])

    def _build_bike(self, shop: Shop, data: dict) -> Bike:
        cover = data.get('cover_image') or ''
        images = data.get('images') or []
        if not cover and images:
            cover = images[0]
        if not cover:
            raise BikeServiceError('请上传封面或展示图')
        return Bike(
            shop=shop,
            brand_id=data.get('brand_id'),
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            register_date=data.get('register_date'),
            displacement=data['displacement'],
            mileage=data.get('mileage', 0),
            transfer_count=data.get('transfer_count', 0),
            price=data['price'],
            can_transfer=data.get('can_transfer', True),
            negotiable=data.get('negotiable', True),
            engine_status=data.get('engine_status', ''),
            suspension_status=data.get('suspension_status', ''),
            brake_status=data.get('brake_status', ''),
            electrical_status=data.get('electrical_status', ''),
            frame_status=data.get('frame_status', ''),
            modification=data.get('modification', ''),
            defects=data.get('defects', ''),
            maintenance=data.get('maintenance', ''),
            delivery_method=data.get('delivery_method', ''),
            fee_note=data.get('fee_note', ''),
            after_sale=data.get('after_sale', ''),
            cover_image=cover,
        )

    def _apply_bike_fields(self, bike: Bike, data: dict) -> None:
        simple_fields = [
            'brand_id', 'brand', 'model', 'year', 'register_date', 'displacement',
            'mileage', 'transfer_count', 'price', 'can_transfer', 'negotiable',
            'engine_status', 'suspension_status', 'brake_status', 'electrical_status',
            'frame_status', 'modification', 'defects', 'maintenance',
            'delivery_method', 'fee_note', 'after_sale', 'cover_image',
        ]
        for field in simple_fields:
            if field in data:
                setattr(bike, field, data[field])

    def _sync_media(self, bike: Bike, data: dict) -> None:
        bike.media_items.filter(is_deleted=False).update(is_deleted=True)
        cover_url = data.get('cover_image') or bike.cover_image
        if cover_url:
            BikeMedia.objects.create(
                bike=bike,
                shop=bike.shop,
                media_type=BikeMedia.MediaType.COVER,
                url=cover_url,
                sort_order=0,
            )
        for idx, url in enumerate(data.get('images') or []):
            BikeMedia.objects.create(
                bike=bike,
                shop=bike.shop,
                media_type=BikeMedia.MediaType.DISPLAY,
                url=url,
                sort_order=idx,
            )
        for idx, url in enumerate(data.get('condition_images') or []):
            BikeMedia.objects.create(
                bike=bike,
                shop=bike.shop,
                media_type=BikeMedia.MediaType.CONDITION,
                url=url,
                sort_order=idx,
            )
        if not bike.cover_image and cover_url:
            bike.cover_image = cover_url
            bike.save(update_fields=['cover_image', 'updated_at'])
