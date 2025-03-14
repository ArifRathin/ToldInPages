# Generated by Django 5.1.5 on 2025-01-25 06:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booklets', '0003_booklet_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='booklet',
            constraint=models.UniqueConstraint(fields=('title', 'user_id'), name='unique_title_constraint'),
        ),
    ]
