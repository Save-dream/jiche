"""初始化可登录账号（账号密码），不写入演示车源/留言等业务测试数据。"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.shops.models import Shop


# 初始账号清单（可按需改密码后重跑：会更新已存在账号的密码与角色）
INIT_ACCOUNTS = [
    {
        'username': 'admin',
        'password': 'Jiche@Admin2026',
        'nickname': '平台管理员',
        'is_staff': True,
        'is_super_staff': True,
        'shop_status': User.ShopStatus.NORMAL,
        'role_label': '平台管理员',
    },
    {
        'username': 'shop',
        'password': 'Jiche@Shop2026',
        'nickname': '商家账号',
        'is_staff': False,
        'is_super_staff': False,
        'shop_status': User.ShopStatus.APPROVED,
        'role_label': '已入驻商家',
        'create_shop': True,
        'shop_name': '我的店铺（请在商家后台修改）',
    },
    {
        'username': 'user',
        'password': 'Jiche@User2026',
        'nickname': '普通用户',
        'is_staff': False,
        'is_super_staff': False,
        'shop_status': User.ShopStatus.NORMAL,
        'role_label': '普通用户',
    },
]


class Command(BaseCommand):
    help = '创建/重置账号密码登录用的初始账号（不含演示业务数据）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='若账号已存在，强制重置为命令内置密码',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset_password = options['reset_password']
        rows = []

        for item in INIT_ACCOUNTS:
            username = item['username']
            user = User.objects.filter(internal_username=username, is_deleted=False).first()
            created = False
            if user is None:
                user = User.objects.create_user(
                    internal_username=username,
                    password=item['password'],
                    nickname=item['nickname'],
                    is_staff=item['is_staff'],
                    is_super_staff=item['is_super_staff'],
                    shop_status=item['shop_status'],
                    is_active=True,
                )
                created = True
            else:
                user.nickname = item['nickname']
                user.is_staff = item['is_staff']
                user.is_super_staff = item['is_super_staff']
                user.shop_status = item['shop_status']
                user.is_active = True
                update_fields = [
                    'nickname', 'is_staff', 'is_super_staff',
                    'shop_status', 'is_active', 'updated_at',
                ]
                if reset_password or not user.has_usable_password():
                    user.set_password(item['password'])
                    update_fields.append('password')
                user.save(update_fields=update_fields)

            if item.get('create_shop'):
                shop = None
                if user.shop_id:
                    shop = Shop.objects.filter(id=user.shop_id, is_deleted=False).first()
                if shop is None:
                    shop = Shop.objects.filter(user=user, is_deleted=False).first()
                if shop is None:
                    shop = Shop.objects.create(
                        user=user,
                        name=item.get('shop_name') or f'{user.nickname}的店铺',
                        shop_type=Shop.ShopType.PERSONAL,
                        contact_name=user.nickname or username,
                        phone=user.phone or '13800000000',
                        wechat_qrcode='',
                        shop_status=Shop.ShopStatus.NORMAL,
                        approved_at=timezone.now(),
                    )
                if user.shop_id != shop.id or user.shop_status != User.ShopStatus.APPROVED:
                    user.shop_id = shop.id
                    user.shop_status = User.ShopStatus.APPROVED
                    user.save(update_fields=['shop_id', 'shop_status', 'updated_at'])

            rows.append({
                'username': username,
                'password': item['password'],
                'role': item['role_label'],
                'created': created,
            })

        self.stdout.write(self.style.SUCCESS('\n======== 初始登录账号 ========'))
        self.stdout.write(f'{"账号":<12} {"密码":<20} {"角色":<12} 状态')
        self.stdout.write('-' * 56)
        for row in rows:
            state = '新建' if row['created'] else ('已更新' if reset_password else '已存在')
            self.stdout.write(
                f'{row["username"]:<12} {row["password"]:<20} {row["role"]:<12} {state}'
            )
        self.stdout.write(self.style.SUCCESS('================================\n'))
        self.stdout.write('登录接口: POST /api/auth/login/  body: {"username","password"}')
        self.stdout.write('提示: 未加 --reset-password 时，已存在账号不会改密码。')
        self.stdout.write('      强制重置密码请执行: python manage.py create_init_accounts --reset-password')
