# Generated by Django 5.1.5 on 2025-03-17 00:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
        ("users", "0002_consumer_images"),
    ]

    operations = [
        migrations.CreateModel(
            name="Merchant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shop_name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Order_Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("price", models.FloatField(default=0)),
                ("quantity", models.FloatField(default=0)),
                ("unit_price", models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("paid_price", models.FloatField(default=0)),
                ("paid_time", models.DateTimeField(auto_now_add=True)),
                ("paid_state", models.CharField(max_length=45)),
            ],
        ),
        migrations.RemoveField(
            model_name="order",
            name="consumerid",
        ),
        migrations.AddField(
            model_name="order",
            name="consumer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.consumer",
            ),
        ),
    ]
