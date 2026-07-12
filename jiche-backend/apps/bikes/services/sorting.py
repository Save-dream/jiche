from typing import Iterable, List, Optional

from django.db.models import Case, F, IntegerField, QuerySet, Value, When
from django.utils import timezone

from apps.bikes.models import Bike


def bike_status_sort_key(status: int) -> int:
    if status == Bike.BikeStatus.ON_SALE:
        return 0
    if status == Bike.BikeStatus.SOLD:
        return 1
    return 2


def apply_bike_sorting(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        _status_order=Case(
            When(bike_status=Bike.BikeStatus.ON_SALE, then=Value(0)),
            When(bike_status=Bike.BikeStatus.SOLD, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
    ).order_by('_status_order', F('published_at').desc(nulls_last=True), '-created_at')


def filter_shop_bikes(
    shop_id: int,
    *,
    c_end_only: bool = False,
    status_filter: Optional[int] = None,
    include_deleted: bool = False,
) -> QuerySet:
    qs = Bike.objects.filter(shop_id=shop_id).select_related('shop')
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    if c_end_only:
        qs = qs.filter(bike_status__in=[Bike.BikeStatus.ON_SALE, Bike.BikeStatus.SOLD])
    elif status_filter:
        qs = qs.filter(bike_status=status_filter)
    return apply_bike_sorting(qs)
