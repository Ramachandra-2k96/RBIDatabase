# Generated by Django 4.2.9 on 2024-03-04 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newbank', '0007_userprofile_accounts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='user',
        ),
    ]
