# Generated by Django 2.2.24 on 2021-08-26 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20210824_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
