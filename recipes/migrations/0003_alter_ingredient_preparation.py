# Generated by Django 3.2.5 on 2021-08-03 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='preparation',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
