from django.core.management.base import BaseCommand

from apps.accounts.models import User


class Command(BaseCommand):
    help = '初始化预置超级管理员（微信 unionid 绑定）'

    def add_arguments(self, parser):
        parser.add_argument('--unionid', required=True, help='微信 unionid')
        parser.add_argument('--nickname', default='平台管理员', help='管理员昵称')
        parser.add_argument('--phone', default=None, help='手机号')

    def handle(self, *args, **options):
        unionid = options['unionid']
        user, created = User.objects.get_or_create(
            unionid=unionid,
            defaults={
                'internal_username': f'admin_{unionid[:16]}',
                'nickname': options['nickname'],
                'phone': options['phone'],
                'is_staff': True,
                'is_super_staff': True,
            },
        )
        if not created:
            user.is_staff = True
            user.is_super_staff = True
            user.nickname = options['nickname']
            if options['phone']:
                user.phone = options['phone']
            user.save()
            self.stdout.write(self.style.WARNING(f'已更新超级管理员: id={user.id} unionid={unionid}'))
        else:
            user.set_unusable_password()
            user.save()
            self.stdout.write(self.style.SUCCESS(f'已创建超级管理员: id={user.id} unionid={unionid}'))
