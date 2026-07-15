from django.db import transaction

from apps.accounts.models import User
from apps.bikes.models import Bike
from apps.bikes.services.bike_service import serialize_bike
from apps.favorites.models import Favorite


class FavoriteServiceError(Exception):
    pass


class FavoriteService:
    def list_favorites(self, user: User) -> dict:
        favorites = Favorite.objects.filter(
            user=user,
            is_deleted=False,
        ).select_related('bike', 'bike__shop').order_by('-created_at')
        result = []
        seen_bike_ids = set()
        for fav in favorites:
            bike = fav.bike
            if bike.id in seen_bike_ids:
                continue
            seen_bike_ids.add(bike.id)
            if bike.is_deleted:
                result.append({
                    'id': bike.id,
                    'shop_id': bike.shop_id,
                    'shop_name': bike.shop.name if bike.shop_id else '',
                    'unavailable': True,
                    'brand': bike.brand,
                    'model': bike.model,
                    'is_deleted': 1,
                })
            else:
                result.append(serialize_bike(bike))
        return {'list': result, 'total': len(result)}

    @transaction.atomic
    def add_favorite(self, user: User, bike_id: int) -> dict:
        try:
            bike = Bike.objects.select_related('shop').get(pk=bike_id, is_deleted=False)
        except Bike.DoesNotExist:
            raise FavoriteServiceError('车辆不存在')
        fav, created = Favorite.objects.get_or_create(
            user=user,
            bike=bike,
            defaults={'shop': bike.shop, 'is_deleted': False},
        )
        if not created:
            if not fav.is_deleted:
                raise FavoriteServiceError('已在收藏夹中')
            fav.is_deleted = False
            fav.shop = bike.shop
            fav.save(update_fields=['is_deleted', 'shop'])
        return serialize_bike(bike)

    @transaction.atomic
    def remove_favorite(self, user: User, bike_id: int) -> None:
        updated = Favorite.objects.filter(
            user=user,
            bike_id=bike_id,
            is_deleted=False,
        ).update(is_deleted=True)
        if not updated:
            raise FavoriteServiceError('收藏不存在')
