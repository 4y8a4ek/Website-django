# Generated by Django 5.1.4 on 2025-04-16 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseprogress',
            name='current_block',
            field=models.IntegerField(default=0),
        ),
    ]
