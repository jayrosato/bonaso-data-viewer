# Generated by Django 4.2.20 on 2025-06-03 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0033_remove_formlogic_limit_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='flag',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
