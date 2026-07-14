from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ban_reason',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='封禁原因'),
        ),
        migrations.AddField(
            model_name='user',
            name='banned_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='封禁时间'),
        ),
        migrations.AddField(
            model_name='user',
            name='delete_reason',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='删除原因'),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='删除时间'),
        ),
    ]
