# Generated by Django 4.0.5 on 2022-10-27 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NP', 'Not processed'), ('CK', 'Cooking'), ('DL', 'Delivering'), ('CP', 'Completed')], default='NP', max_length=13, verbose_name='Статус заказа'),
        ),
    ]
