# Generated by Django 4.1 on 2022-09-06 09:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_productinfo_item_id_productinfo_model_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='type',
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('customer', 'Покупатель'), ('shop', 'Магазин')], default='customer', max_length=30, verbose_name='Тип пользователя'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
