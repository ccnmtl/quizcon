# Generated by Django 2.2.24 on 2021-06-14 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0003_quiz_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quiz_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quiz',
            name='modified_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quiz_modified_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
