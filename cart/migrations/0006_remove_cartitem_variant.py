# Generated by Django 5.1.5 on 2025-03-19 23:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0005_remove_cartitem_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cartitem",
            name="variant",
        ),
    ]
