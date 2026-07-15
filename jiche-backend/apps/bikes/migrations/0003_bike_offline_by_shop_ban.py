from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bikes', '0002_sharelink'),
    ]

    operations = [
        migrations.AddField(
            model_name='bike',
            name='offline_by_shop_ban',
            field=models.BooleanField(
                default=False,
                help_text='解封时可据此恢复上架；商家手动下架不标记此项',
                verbose_name='因店铺封禁而下架',
            ),
        ),
    ]
