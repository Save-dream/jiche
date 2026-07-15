from __future__ import annotations

import hashlib
import hmac
import secrets
import string
import time
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.accounts.models import User
from apps.bikes.models import Bike, ShareLink
from apps.shops.models import Shop


class ShareServiceError(Exception):
    pass


ALPHABET = string.ascii_letters + string.digits


class ShareService:
    @property
    def ttl_seconds(self) -> int:
        days = int(getattr(settings, 'SHARE_SIGN_TTL_DAYS', 7) or 7)
        return days * 24 * 3600

    def make_sign(self, shop_id: int, bike_id: Optional[int], timestamp: int) -> str:
        bike_part = str(bike_id or 0)
        message = f'{shop_id}_{bike_part}_{timestamp}'.encode('utf-8')
        secret = settings.SECRET_KEY.encode('utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    def verify_sign(
        self,
        shop_id: int,
        bike_id: Optional[int],
        timestamp: str | int | None,
        sign: str | None,
    ) -> None:
        if not timestamp or not sign:
            raise ShareServiceError('分享链接签名无效')
        try:
            ts = int(timestamp)
        except (TypeError, ValueError) as exc:
            raise ShareServiceError('分享链接已失效') from exc
        now = int(time.time())
        if ts > now + 300 or now - ts > self.ttl_seconds:
            raise ShareServiceError('分享链接已过期，请联系商家获取最新链接')
        expected = self.make_sign(shop_id, bike_id, ts)
        if not hmac.compare_digest(expected, str(sign)):
            raise ShareServiceError('分享链接签名无效')

    def _generate_short_code(self, length: int = 6) -> str:
        for _ in range(20):
            code = ''.join(secrets.choice(ALPHABET) for _ in range(length))
            if not ShareLink.objects.filter(short_code=code).exists():
                return code
        raise ShareServiceError('短链生成失败，请重试')

    def _web_base(self) -> str:
        return getattr(settings, 'SHARE_WEB_BASE_URL', 'http://localhost:5173').rstrip('/')

    @transaction.atomic
    def create_bike_share_link(self, shop: Shop, bike_id: int, user: User) -> dict:
        try:
            bike = Bike.objects.get(pk=bike_id, shop=shop, is_deleted=False)
        except Bike.DoesNotExist as exc:
            raise ShareServiceError('车辆不存在') from exc
        if bike.bike_status == Bike.BikeStatus.FORCE_OFF:
            raise ShareServiceError('违规下架车辆不可分享')

        timestamp = int(time.time())
        sign = self.make_sign(shop.id, bike.id, timestamp)
        expired_at = timezone.now() + timedelta(seconds=self.ttl_seconds)
        link = ShareLink.objects.create(
            short_code=self._generate_short_code(),
            shop=shop,
            bike=bike,
            timestamp=timestamp,
            sign=sign,
            expired_at=expired_at,
            created_by=user,
        )
        base = self._web_base()
        signed_path = (
            f'/bike/{bike.id}?shop_id={shop.id}&timestamp={timestamp}&sign={sign}'
        )
        return {
            'short_code': link.short_code,
            'short_url': f'{base}/s/{link.short_code}',
            'full_url': f'{base}{signed_path}',
            'path': signed_path,
            'shop_id': shop.id,
            'bike_id': bike.id,
            'timestamp': timestamp,
            'sign': sign,
            'expired_at': expired_at.strftime('%Y-%m-%d %H:%M'),
        }

    @transaction.atomic
    def resolve_short_code(self, short_code: str) -> dict:
        try:
            link = ShareLink.objects.select_related('bike', 'shop').get(short_code=short_code)
        except ShareLink.DoesNotExist as exc:
            raise ShareServiceError('链接不存在或已失效') from exc

        if timezone.now() > link.expired_at:
            raise ShareServiceError('链接已过期，请联系商家获取最新链接')

        shop = link.shop
        if shop.is_deleted:
            raise ShareServiceError('店铺已注销，暂不可访问！')
        if shop.shop_status == Shop.ShopStatus.BANNED:
            raise ShareServiceError('店铺已封禁，暂不可访问！')

        self.verify_sign(link.shop_id, link.bike_id, link.timestamp, link.sign)
        ShareLink.objects.filter(pk=link.id).update(click_count=F('click_count') + 1)

        if link.bike_id:
            if link.bike.is_deleted or link.bike.bike_status not in (
                Bike.BikeStatus.ON_SALE,
                Bike.BikeStatus.SOLD,
            ):
                raise ShareServiceError('车辆不存在或已下架')
            path = (
                f'/bike/{link.bike_id}'
                f'?shop_id={link.shop_id}&timestamp={link.timestamp}&sign={link.sign}'
            )
            return {
                'type': 'bike',
                'shop_id': link.shop_id,
                'bike_id': link.bike_id,
                'timestamp': link.timestamp,
                'sign': link.sign,
                'path': path,
            }

        path = f'/shop/{link.shop_id}'
        return {
            'type': 'shop',
            'shop_id': link.shop_id,
            'bike_id': None,
            'timestamp': link.timestamp,
            'sign': link.sign,
            'path': path,
        }
