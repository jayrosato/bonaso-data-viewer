# Generated by Django 5.2 on 2025-04-22 10:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0007_alter_answer_open_answer_alter_answer_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='formquestion',
            name='visible_if_answer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formquestion',
            name='visible_if_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='question_logic', to='forms.question'),
        ),
        migrations.AlterField(
            model_name='formquestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='forms.question'),
        ),
    ]
