# Generated by Django 5.2 on 2025-04-22 08:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0006_alter_form_options_alter_response_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='open_answer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='forms.option'),
        ),
    ]
