# Generated by Django 5.1.7 on 2025-03-12 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='age',
            field=models.IntegerField(default=18),
        ),
    ]
