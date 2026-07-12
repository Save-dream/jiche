from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0002_usershopvisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopapplication',
            name='name',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='商家名称'),
        ),
    ]
