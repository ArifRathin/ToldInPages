# Generated by Django 5.1.5 on 2025-02-02 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booklets', '0006_remove_booklet_unique_title_constraint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booklet',
            name='read',
            field=models.BigIntegerField(default=0),
        ),
    ]
