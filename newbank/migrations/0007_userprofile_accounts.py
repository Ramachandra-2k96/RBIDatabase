# Generated by Django 4.2.9 on 2024-03-04 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newbank', '0006_alter_bank_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='accounts',
            field=models.ManyToManyField(related_name='user_profiles', to='newbank.account'),
        ),
    ]
