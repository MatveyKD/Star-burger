# Generated by Django 4.0.5 on 2022-11-23 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_alter_orderproduct_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='payment',
            new_name='payment_method',
        ),
    ]
