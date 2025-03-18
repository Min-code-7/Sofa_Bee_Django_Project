# Generated by Django 5.1.2 on 2025-03-18 00:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_rename_consumer_id_address_consumer'),
        ('profiles', '0001_initial'),
        ('users', '0002_consumer_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50, null=True)),
                ('shop_description', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.BooleanField(default=False)),
                ('total_price', models.FloatField(default=0)),
                ('paid_time', models.DateTimeField(auto_now_add=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='addresses.address')),
                ('consumer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.consumer')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_price', models.FloatField(default=0)),
                ('paid_time', models.DateTimeField(auto_now_add=True)),
                ('paid_status', models.CharField(max_length=45)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.order')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.FloatField(default=0)),
                ('image', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=45, null=True)),
                ('merchant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.merchant')),
            ],
        ),
        migrations.CreateModel(
            name='Order_Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0)),
                ('quantity', models.FloatField(default=0)),
                ('unit_price', models.FloatField(default=0)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.product')),
            ],
        ),
    ]
