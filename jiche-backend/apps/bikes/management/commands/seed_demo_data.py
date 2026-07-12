"""预制演示车源、收藏与留言，可通过页面正常删除。"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.bikes.models import Bike, BikeMedia
from apps.favorites.models import Favorite
from apps.messaging.models import MessageItem, MessageThread
from apps.shops.models import Shop

IMG = 'https://placehold.co/800x600?text={text}'


def _bike_images(text: str, count: int = 3) -> list[str]:
    return [IMG.format(text=f'{text}-{i + 1}') for i in range(count)]


DEMO_BIKES = [
    {
        'brand': '本田',
        'model': 'CB400',
        'year': 2020,
        'displacement': '400cc',
        'mileage': 12000,
        'price': 32800,
        'bike_status': Bike.BikeStatus.ON_SALE,
        'view_count': 156,
    },
    {
        'brand': '本田',
        'model': 'CBR600RR',
        'year': 2019,
        'displacement': '600cc',
        'mileage': 18000,
        'price': 45800,
        'bike_status': Bike.BikeStatus.SOLD,
        'view_count': 89,
    },
    {
        'brand': '川崎',
        'model': 'Z900',
        'year': 2021,
        'displacement': '900cc',
        'mileage': 9500,
        'price': 56800,
        'bike_status': Bike.BikeStatus.ON_SALE,
        'view_count': 203,
    },
]

COMMON_FIELDS = {
    'transfer_count': 0,
    'can_transfer': True,
    'negotiable': True,
    'engine_status': '原厂运转正常，保养及时，无异响',
    'suspension_status': '前后减震原厂，无漏油',
    'brake_status': '刹车片剩余约 70%',
    'electrical_status': '电控系统正常，无故障灯',
    'frame_status': '车架无变形，无事故记录',
    'modification': '无',
    'defects': '轻微使用痕迹，无结构性损伤',
    'maintenance': '每 5000km 保养，近期已换机油',
    'delivery_method': '自提/物流',
    'fee_note': '含过户手续',
    'after_sale': '7 天质量问题协商处理',
}


class Command(BaseCommand):
    help = '预制演示车源、收藏与留言（需先运行 seed_auth_demo、seed_catalog）'

    def handle(self, *args, **options):
        shop = Shop.objects.filter(name='极速摩托行', is_deleted=False).first()
        if not shop:
            self.stderr.write(self.style.ERROR('未找到演示商家，请先运行: python manage.py seed_auth_demo'))
            return

        normal_user = User.objects.filter(unionid='placeholder_user_unionid', is_deleted=False).first()
        now = timezone.now()
        created_bikes = []

        for spec in DEMO_BIKES:
            images = _bike_images(f"{spec['brand']}{spec['model']}", 3)
            defaults = {
                **COMMON_FIELDS,
                **spec,
                'cover_image': images[0],
                'is_deleted': False,
                'published_at': now,
            }
            bike, created = Bike.objects.update_or_create(
                shop=shop,
                brand=spec['brand'],
                model=spec['model'],
                year=spec['year'],
                defaults=defaults,
            )
            bike.media_items.filter(is_deleted=False).update(is_deleted=True)
            BikeMedia.objects.create(
                bike=bike, shop=shop,
                media_type=BikeMedia.MediaType.COVER,
                url=images[0], sort_order=0,
            )
            for idx, url in enumerate(images):
                BikeMedia.objects.create(
                    bike=bike, shop=shop,
                    media_type=BikeMedia.MediaType.DISPLAY,
                    url=url, sort_order=idx,
                )
            action = '创建' if created else '更新'
            created_bikes.append(bike)
            self.stdout.write(self.style.SUCCESS(
                f'{action}演示车源 id={bike.id} {bike.brand} {bike.model} status={bike.bike_status}'
            ))

        if normal_user and created_bikes:
            cb400 = next((b for b in created_bikes if b.model == 'CB400'), created_bikes[0])
            fav, fav_created = Favorite.objects.get_or_create(
                user=normal_user,
                bike=cb400,
                defaults={'shop': shop, 'is_deleted': False},
            )
            if not fav_created and fav.is_deleted:
                fav.is_deleted = False
                fav.save(update_fields=['is_deleted'])
            self.stdout.write(self.style.SUCCESS(
                f'{"创建" if fav_created else "更新"}演示收藏 user={normal_user.id} bike={cb400.id}'
            ))

            thread, thread_created = MessageThread.objects.get_or_create(
                user=normal_user,
                bike=cb400,
                defaults={
                    'shop': shop,
                    'contact_phone': normal_user.phone or '13600000001',
                    'thread_status': MessageThread.ThreadStatus.READ_NO_REPLY,
                    'unread_count_shop': 1,
                    'last_message_at': now,
                    'last_message_preview': '这辆车还在吗？可以预约看车吗？',
                },
            )
            if thread_created or not thread.messages.filter(is_deleted=False).exists():
                MessageItem.objects.create(
                    thread=thread,
                    shop=shop,
                    sender=normal_user,
                    sender_type=MessageItem.SenderType.USER,
                    content='这辆车还在吗？可以预约看车吗？',
                )
            self.stdout.write(self.style.SUCCESS(
                f'演示留言 thread_id={thread.id} bike={cb400.id}'
            ))

        self.stdout.write(self.style.WARNING(
            '演示数据可通过商家后台删除车源、用户端取消收藏等方式清除'
        ))
        ids = ', '.join(str(b.id) for b in created_bikes)
        self.stdout.write(self.style.SUCCESS(f'演示车源 ID：{ids}（shop_id={shop.id}）'))
