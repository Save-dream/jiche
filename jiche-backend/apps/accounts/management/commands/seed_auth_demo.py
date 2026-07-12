from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.shops.models import Shop, ShopApplication


class Command(BaseCommand):
    help = '初始化认证模块演示账号（预置超管 + 普通/待审/商家用户）'

    def handle(self, *args, **options):
        admin, admin_created = User.objects.get_or_create(
            unionid='placeholder_admin_unionid',
            defaults={
                'internal_username': 'admin_placeholder',
                'nickname': '平台管理员',
                'phone': '13999999999',
                'mp_openid': 'placeholder_mp_admin',
                'is_staff': True,
                'is_super_staff': True,
            },
        )
        if not admin_created:
            admin.is_staff = True
            admin.is_super_staff = True
            admin.nickname = '平台管理员'
            admin.save()
        admin.set_unusable_password()
        admin.save(update_fields=['password'])

        normal, normal_created = User.objects.get_or_create(
            unionid='placeholder_user_unionid',
            defaults={
                'internal_username': 'user_placeholder',
                'nickname': '普通用户',
                'phone': '13600000001',
                'mp_openid': 'placeholder_mp_user',
                'shop_status': User.ShopStatus.NORMAL,
            },
        )
        if normal_created:
            normal.set_unusable_password()
            normal.save(update_fields=['password'])

        pending, _ = User.objects.get_or_create(
            unionid='dev_pending_unionid',
            defaults={
                'internal_username': 'dev_pending_user',
                'nickname': '待审核商家',
                'phone': '13600000002',
                'mp_openid': 'dev_mp_pending',
                'shop_status': User.ShopStatus.PENDING,
            },
        )
        pending.shop_status = User.ShopStatus.PENDING
        pending.save(update_fields=['shop_status', 'updated_at'])
        pending_app = ShopApplication.objects.filter(
            user=pending,
            application_status=ShopApplication.ApplicationStatus.PENDING,
            is_deleted=False,
        ).first()
        app_defaults = {
            'name': '待审核演示车行',
            'shop_type': ShopApplication.ShopType.PERSONAL,
            'contact_name': '待审核商家',
            'phone': '13600000002',
            'address': '广州市天河区',
            'main_models': '本田、雅马哈',
            'description': '开发演示待审核申请',
            'wechat_qrcode': '/media/uploads/dev_pending_qr.jpg',
        }
        if pending_app:
            for key, value in app_defaults.items():
                setattr(pending_app, key, value)
            pending_app.save()
        else:
            ShopApplication.objects.create(user=pending, **app_defaults)

        shop_user, _ = User.objects.get_or_create(
            unionid='dev_shop_unionid',
            defaults={
                'internal_username': 'dev_shop_user',
                'nickname': '极速摩托行老板',
                'phone': '13800138001',
                'mp_openid': 'dev_mp_shop',
                'shop_status': User.ShopStatus.APPROVED,
            },
        )
        shop, _ = Shop.objects.get_or_create(
            user=shop_user,
            defaults={
                'name': '极速摩托行',
                'shop_type': Shop.ShopType.PERSONAL,
                'contact_name': '张老板',
                'phone': '13800138001',
                'address': '广州市天河区车陂路168号',
                'main_models': '本田、雅马哈中大排量',
                'description': '开发演示商家',
                'wechat_qrcode': '/media/uploads/dev_shop_qr.jpg',
                'shop_status': Shop.ShopStatus.NORMAL,
                'approved_at': timezone.now(),
            },
        )
        shop_user.shop_status = User.ShopStatus.APPROVED
        shop_user.shop_id = shop.id
        shop_user.save(update_fields=['shop_status', 'shop_id', 'updated_at'])

        banned_user, _ = User.objects.get_or_create(
            unionid='dev_banned_unionid',
            defaults={
                'internal_username': 'dev_banned_user',
                'nickname': '封禁商家演示',
                'phone': '13600000003',
                'mp_openid': 'dev_mp_banned',
                'shop_status': User.ShopStatus.BANNED,
                'shop_id': shop.id,
            },
        )
        banned_user.shop_status = User.ShopStatus.BANNED
        banned_user.shop_id = shop.id
        banned_user.save(update_fields=['shop_status', 'shop_id', 'updated_at'])

        self.stdout.write(self.style.SUCCESS(
            f'预置超管 id={admin.id} unionid=placeholder_admin_unionid'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'普通用户 id={normal.id} unionid=placeholder_user_unionid'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'待审核商家 id={pending.id} unionid=dev_pending_unionid'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'入驻商家 id={shop_user.id} shop_id={shop.id} unionid=dev_shop_unionid'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'封禁商家 id={banned_user.id} unionid=dev_banned_unionid'
        ))
        self.stdout.write(self.style.WARNING(
            '微信凭证当前为占位值；Dev 角色切换请使用 NavBar [Dev] 或 /login 模拟扫码'
        ))
        self.stdout.write(self.style.WARNING(
            '演示车源请运行: python manage.py seed_demo_data'
        ))
