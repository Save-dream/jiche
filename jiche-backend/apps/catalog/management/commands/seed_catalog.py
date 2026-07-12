from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, BrandModel

MOCK_BRANDS = [
    (1, '本田', ['CB400', 'CB500F', 'CBR600RR', 'NC750X', 'CRF1100L']),
    (2, '雅马哈', ['MT-07', 'MT-09', 'YZF-R1', 'NMAX155', 'XMAX300']),
    (3, '铃木', ['GSX-R750', 'V-STROM650', 'BOULEVARD']),
    (4, '川崎', ['Z900', 'Ninja 400', 'Versys 650', 'Z H2']),
    (5, '宝马', ['R1250GS', 'S1000RR', 'F850GS']),
    (6, '哈雷', ['Sportster', 'Fat Boy', 'Road King']),
    (7, '杜卡迪', ['Panigale V4', 'Monster', 'Multistrada']),
    (8, '春风', ['450SR', '800MT', 'NK800']),
    (9, '钱江', ['QJ900GS', 'SR500']),
    (10, '贝纳利', ['502C', 'Leoncino500']),
]


class Command(BaseCommand):
    help = '初始化品牌与车型字典（对齐 mock.js mockBrands / mockModels）'

    def handle(self, *args, **options):
        for sort_order, (brand_id, name, models) in enumerate(MOCK_BRANDS, start=1):
            brand, created = Brand.objects.update_or_create(
                id=brand_id,
                defaults={
                    'name': name,
                    'sort_order': sort_order,
                    'is_enabled': True,
                },
            )
            for model_name in models:
                BrandModel.objects.update_or_create(
                    brand=brand,
                    name=model_name,
                    defaults={'is_enabled': True},
                )
            action = '创建' if created else '更新'
            self.stdout.write(f'{action}品牌 {brand.name}，{len(models)} 个车型')

        self.stdout.write(self.style.SUCCESS('品牌车型字典初始化完成'))
