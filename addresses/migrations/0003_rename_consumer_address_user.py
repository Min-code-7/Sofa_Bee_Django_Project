# Generated by Django 5.1.2 on 2025-03-19 01:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_alter_address_consumer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='consumer',
            new_name='user',
        ),
    ]
