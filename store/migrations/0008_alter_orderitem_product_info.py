# Generated by Django 4.1 on 2022-09-10 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_orderitem_unique_order_item_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product_info',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.productinfo', verbose_name='Информация о продукте'),
        ),
    ]
