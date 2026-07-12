import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shops', '0003_shopapplication_name'),
        ('bikes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_code', models.CharField(max_length=16, unique=True, verbose_name='短链码')),
                ('timestamp', models.BigIntegerField(verbose_name='签名时间戳')),
                ('sign', models.CharField(max_length=128, verbose_name='HMAC 签名')),
                ('expired_at', models.DateTimeField(verbose_name='过期时间')),
                ('click_count', models.PositiveIntegerField(default=0, verbose_name='点击次数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('bike', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='share_links', to='bikes.bike', verbose_name='车源')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_share_links', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='share_links', to='shops.shop', verbose_name='商家')),
            ],
            options={
                'verbose_name': '分享短链',
                'verbose_name_plural': '分享短链',
                'db_table': 'share_link',
                'indexes': [
                    models.Index(fields=['shop', 'bike'], name='share_link_shop_id_7f2b0c_idx'),
                    models.Index(fields=['expired_at'], name='share_link_expired_3a1d9e_idx'),
                ],
            },
        ),
    ]
