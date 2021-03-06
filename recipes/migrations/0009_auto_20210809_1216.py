# Generated by Django 3.2.5 on 2021-08-09 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_ingredient_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.FloatField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.CharField(blank=True, default='', max_length=15),
        ),
    ]
